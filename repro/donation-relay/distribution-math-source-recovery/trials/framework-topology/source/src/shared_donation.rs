//! Common donation context, wire-neutral arguments and result recovered from disassembly.
use anchor_lang::prelude::*;
use anchor_spl::token_interface::{TokenAccount,Mint};
use crate::anchor_framework::{EpochTrackerV1,EpochTrackerV1State,DebouncerV1,DebouncerV1State,MintWhitelistV1};
use crate::business_error_codes::ErrorCode as Code;
pub struct DonationContext<'a,'info> {
 pub epoch_tracker:&'a mut Account<'info,EpochTrackerV1>,pub debouncer:&'a mut Account<'info,DebouncerV1>,
 pub from:&'a Signer<'info>,pub mint_whitelist:&'a Account<'info,MintWhitelistV1>,
 pub debouncer_token_account:AccountInfo<'info>,pub mint:AccountInfo<'info>,pub from_token_account:AccountInfo<'info>,pub token_program:AccountInfo<'info>,
}
pub struct DonationArgs {pub config_id:[u8;32],pub amount:u64,pub message:String,pub tip_bps:u16,pub epoch_tracker_bump:u8,pub debouncer_bump:u8}
pub struct DonationAmounts {pub epoch:u128,pub gross_amount:u64,pub tip:u64}
macro_rules! source_error {
 ($code:ident,$file:literal,$line:literal)=>{anchor_lang::error::Error::from(anchor_lang::error::AnchorError {
 error_name:Code::$code.name(),error_code_number:Code::$code.into(),error_msg:Code::$code.to_string(),
 error_origin:Some(anchor_lang::error::ErrorOrigin::Source(anchor_lang::error::Source {filename:$file,line:$line})),compared_values:None,
 })};
}
pub fn check_message(message:&str)->Result<()> {
 if message.len()>=256 {return Err(source_error!(InvalidMessageLength,"programs/contracts/src/tools/checks.rs",55));}Ok(())
}
pub fn check_bps(bps:u16)->Result<()> {
 if bps>10000 {return Err(source_error!(InvalidBps,"programs/contracts/src/tools/checks.rs",192));}Ok(())
}
pub fn deserialize_token_account(info:&AccountInfo)->Result<TokenAccount> {
 let data=info.try_borrow_data()?;
 let result=TokenAccount::try_deserialize(&mut data.as_ref());result
}
pub fn deserialize_mint(info:&AccountInfo)->Result<Mint> {
 let data=info.try_borrow_data()?;
 let result=Mint::try_deserialize(&mut data.as_ref());result
}
pub fn donate_shared(ctx:DonationContext,args:DonationArgs)->Result<DonationAmounts> {
 let mint=*ctx.mint.key;
 check_message(&args.message)?;check_bps(args.tip_bps)?;
 {
  let info=ctx.mint.clone();let owner=*info.owner;
  if owner.to_bytes()!=crate::codec::constants::TOKEN && owner.to_bytes()!=crate::codec::constants::TOKEN2022 {return Err(Code::InvalidTokenProgram.into());}
  if mint.to_bytes()!=crate::codec::constants::NATIVE && mint.to_bytes()!=crate::codec::constants::NATIVE2022 && !ctx.mint_whitelist.mints.contains(&mint) {
   if !crate::mint_policy::typed_mint_safe(&info)? {return Err(source_error!(MintNotSafeForDonation,"programs/contracts/src/tools/checks.rs",184));}
  }
 }
 let tracker=&mut *ctx.epoch_tracker;
 if tracker.state==EpochTrackerV1State::Uninitialized {
  tracker.set_inner(EpochTrackerV1 {bump:args.epoch_tracker_bump,state:EpochTrackerV1State::Initialized,config_id:args.config_id,mint,current_epoch:0});
 }
 let debouncer=&mut *ctx.debouncer;
 if debouncer.state==DebouncerV1State::Uninitialized {
  debouncer.set_inner(DebouncerV1 {bump:args.debouncer_bump,state:DebouncerV1State::Initialized,config_id:args.config_id,mint,total_amount:0});
 }
 if !args.config_id.iter().eq(tracker.config_id.iter()) {return Err(source_error!(InvalidConfigId,"programs/contracts/src/tools/donate/shared.rs",102));}
 if !args.config_id.iter().eq(debouncer.config_id.iter()) {return Err(source_error!(InvalidConfigId,"programs/contracts/src/tools/donate/shared.rs",110));}
 if debouncer.mint!=mint {return Err(source_error!(InvalidMint,"programs/contracts/src/tools/donate/shared.rs",118).with_pubkeys((debouncer.mint,mint)));}
 if debouncer.state!=DebouncerV1State::Initialized {return Err(source_error!(InvalidState,"programs/contracts/src/tools/donate/shared.rs",123));}
 if tracker.mint!=mint {return Err(source_error!(InvalidMint,"programs/contracts/src/tools/donate/shared.rs",127).with_pubkeys((tracker.mint,mint)));}
 if tracker.state!=EpochTrackerV1State::Initialized {return Err(source_error!(InvalidState,"programs/contracts/src/tools/donate/shared.rs",132));}
 let before=deserialize_token_account(&ctx.debouncer_token_account)?.amount;
 let decimals=deserialize_mint(&ctx.mint)?.decimals;
 anchor_spl::token_interface::transfer_checked(CpiContext::new(ctx.token_program.clone(),anchor_spl::token_interface::TransferChecked {
  from:ctx.from_token_account.clone(),mint:ctx.mint.clone(),to:ctx.debouncer_token_account.clone(),authority:ctx.from.to_account_info(),
 }),args.amount,decimals)?;
 let after=deserialize_token_account(&ctx.debouncer_token_account)?.amount;
 let delta=after.checked_sub(before).ok_or(Code::ArithmeticOverflow)?;
 let product=delta.checked_mul(u64::from(args.tip_bps)).ok_or(Code::ArithmeticOverflow)?;
 debouncer.total_amount=debouncer.total_amount.checked_add(delta).ok_or(Code::ArithmeticOverflow)?;
 Ok(DonationAmounts {epoch:tracker.current_epoch,gross_amount:delta,tip:product/10000})
}

//! Typed close-epoch body. Privileged runtime success is not inferred from parser tests.
use anchor_lang::prelude::*;
use crate::anchor_framework::*;
use crate::business_error_codes::ErrorCode as Code;
macro_rules! close_error {($code:ident,$line:literal)=>{anchor_lang::error::Error::from(anchor_lang::error::AnchorError {
 error_name:Code::$code.name(),error_code_number:Code::$code.into(),error_msg:Code::$code.to_string(),
 error_origin:Some(anchor_lang::error::ErrorOrigin::Source(anchor_lang::error::Source {filename:"programs/contracts/src/instructions/v1/relayer_only/close_donation_epoch.rs",line:$line})),compared_values:None})};}
pub fn close_epoch(accounts:&mut CloseDonationEpochV1,args:crate::codec::wire::CloseDonationEpochV1,distribution_bump:u8)->Result<DonationEpochClosedV1Event> {
 let gross=accounts.debouncer.total_amount;
 if gross==0 {return Err(close_error!(InvalidBalance,91));}
 let epoch=accounts.epoch_tracker.current_epoch;
 if args.epoch!=epoch {return Err(close_error!(EpochAlreadyClosed,95));}
 accounts.distribution.set_inner(DistributionV1 {bump:distribution_bump,state:DistributionV1State::Initialized,config_id:accounts.debouncer.config_id,mint:accounts.debouncer.mint,epoch,total_amount:gross});
 let bump=[accounts.debouncer.bump];
 let seeds:&[&[u8]]=&[b"debouncer_v1",accounts.debouncer.config_id.as_ref(),accounts.debouncer.mint.as_ref(),&bump];
 anchor_spl::token_interface::transfer_checked(CpiContext::new_with_signer(accounts.token_program.to_account_info(),anchor_spl::token_interface::TransferChecked {
  from:accounts.debouncer_token_account.to_account_info(),mint:accounts.mint.to_account_info(),to:accounts.distribution_token_account.to_account_info(),authority:accounts.debouncer.to_account_info(),
 },&[seeds]),gross,accounts.mint.decimals)?;
 accounts.debouncer.total_amount=0;
 accounts.epoch_tracker.current_epoch=accounts.epoch_tracker.current_epoch.checked_add(1).ok_or(Code::ArithmeticOverflow)?;
 Ok(DonationEpochClosedV1Event {daas_event_discriminator:DaasEventDiscriminator::DonationEpochClosedV1,config_id:accounts.debouncer.config_id,mint:accounts.debouncer.mint,epoch,gross_epoch_amount:gross})
}

macro_rules! just_error {($code:ident,$line:literal)=>{anchor_lang::error::Error::from(anchor_lang::error::AnchorError {
 error_name:Code::$code.name(),error_code_number:Code::$code.into(),error_msg:Code::$code.to_string(),
 error_origin:Some(anchor_lang::error::ErrorOrigin::Source(anchor_lang::error::Source {filename:"programs/contracts/src/instructions/v1/relayer_only/distribute/just_swap.rs",line:$line})),compared_values:None})};}
pub fn just_swap<'info>(accounts:&mut JustSwapV1<'info>,data:Vec<u8>,remaining:&[AccountInfo<'info>],receipt_bump:u8)->Result<DonationEpochJustSwappedV1Event> {
 if !(accounts.distribution.epoch<accounts.epoch_tracker.current_epoch) {return Err(just_error!(EpochNotClosed,110));}
 if accounts.distribution.state!=DistributionV1State::Initialized {return Err(just_error!(InvalidState,115));}
 if accounts.debouncer.mint!=accounts.distribution.mint {return Err(just_error!(InvalidMint,120).with_pubkeys((accounts.debouncer.mint,accounts.distribution.mint)));}
 if accounts.distribution.mint==Pubkey::new_from_array(crate::codec::constants::SETTLEMENT) {return Err(just_error!(InvalidMint,126).with_pubkeys((accounts.distribution.mint,Pubkey::new_from_array(crate::codec::constants::SETTLEMENT))));}
 let config=accounts.distribution.config_id;let mint=accounts.distribution.mint;
 let epoch=accounts.distribution.epoch.to_le_bytes();let bump=[accounts.distribution.bump];
 let seeds:&[&[u8]]=&[b"distribution_v1",config.as_ref(),mint.as_ref(),&epoch,&bump];
 let output=swap_observed(&accounts.jupiter_program,accounts.distribution.key(),&mut accounts.distribution_token_account,&mut accounts.output_distribution_token_account,remaining,data,&[seeds],accounts.distribution.total_amount)?;
 accounts.swap_receipt.set_inner(SwapReceiptV1 {bump:receipt_bump,distribution:accounts.distribution.key(),swap_output_amount:output});
 accounts.distribution_token_account.reload()?;
 burn_and_close(BurnCloseContext {token:accounts.distribution_token_account.to_account_info(),mint:accounts.mint.to_account_info(),program:accounts.token_program.to_account_info(),authority:accounts.distribution.to_account_info(),destination:accounts.signer.to_account_info()},accounts.distribution_token_account.amount,&[seeds])?;
 Ok(DonationEpochJustSwappedV1Event {daas_event_discriminator:DaasEventDiscriminator::DonationEpochJustSwappedV1,config_id:accounts.distribution.config_id,mint:accounts.distribution.mint,epoch:accounts.distribution.epoch,distribution:accounts.distribution.key(),swap_receipt:accounts.swap_receipt.key(),output_token_account:accounts.output_distribution_token_account.key(),swap_output_amount:output,settlement_mint:accounts.output_mint.key()})
}
macro_rules! jupiter_error {($code:ident,$line:literal)=>{anchor_lang::error::Error::from(anchor_lang::error::AnchorError {
 error_name:Code::$code.name(),error_code_number:Code::$code.into(),error_msg:Code::$code.to_string(),
 error_origin:Some(anchor_lang::error::ErrorOrigin::Source(anchor_lang::error::Source {filename:"programs/contracts/src/cpi/jupiter.rs",line:$line})),compared_values:None})};}
pub fn swap_observed<'info>(program:&AccountInfo<'info>,authority:Pubkey,input:&mut anchor_lang::accounts::interface_account::InterfaceAccount<'info,anchor_spl::token_interface::TokenAccount>,output:&mut anchor_lang::accounts::interface_account::InterfaceAccount<'info,anchor_spl::token_interface::TokenAccount>,remaining:&[AccountInfo<'info>],data:Vec<u8>,seeds:&[&[&[u8]]],expected:u64)->Result<u64> {
 let before_input=input.amount;let before_output=output.amount;
 invoke_jupiter(&program.key(),&authority,remaining,data,seeds)?;
 input.reload()?;output.reload()?;
 let spent=before_input.checked_sub(input.amount).ok_or(Code::ArithmeticOverflow)?;
 if spent!=expected {return Err(jupiter_error!(InputAmountMismatch,92).with_values((spent,expected)));}
 let delta=output.amount.checked_sub(before_output).ok_or(Code::ArithmeticOverflow)?;
 if delta==0 {return Err(jupiter_error!(OutputAmountMustBeGreaterThanZero,103));}Ok(delta)
}
pub fn invoke_jupiter<'info>(program:&Pubkey,authority:&Pubkey,remaining:&[AccountInfo<'info>],data:Vec<u8>,seeds:&[&[&[u8]]])->Result<()> {
 let metas=remaining.iter().map(|a|if a.is_writable {anchor_lang::solana_program::instruction::AccountMeta::new(*a.key,a.key==authority)} else {anchor_lang::solana_program::instruction::AccountMeta::new_readonly(*a.key,a.key==authority)}).collect();
 let infos=remaining.to_vec();
 let ix=anchor_lang::solana_program::instruction::Instruction {program_id:*program,accounts:metas,data};
 if seeds.is_empty() {anchor_lang::solana_program::program::invoke(&ix,&infos)?;} else {anchor_lang::solana_program::program::invoke_signed(&ix,&infos,seeds)?;}Ok(())
}
pub struct BurnCloseContext<'info> {pub token:AccountInfo<'info>,pub mint:AccountInfo<'info>,pub authority:AccountInfo<'info>,pub destination:AccountInfo<'info>,pub program:AccountInfo<'info>}
pub fn burn_and_close<'info>(ctx:BurnCloseContext<'info>,amount:u64,seeds:&[&[&[u8]]])->Result<()> {
 let close_accounts=anchor_spl::token_interface::CloseAccount {account:ctx.token,destination:ctx.destination,authority:ctx.authority};
 if amount!=0 {anchor_spl::token_interface::burn(CpiContext::new_with_signer(ctx.program.clone(),anchor_spl::token_interface::Burn {mint:ctx.mint.clone(),from:close_accounts.account.clone(),authority:close_accounts.authority.clone()},seeds),amount)?;}
 anchor_spl::token_interface::close_account(CpiContext::new_with_signer(ctx.program,close_accounts,seeds))?;Ok(())
}

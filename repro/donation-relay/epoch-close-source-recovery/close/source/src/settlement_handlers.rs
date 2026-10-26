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

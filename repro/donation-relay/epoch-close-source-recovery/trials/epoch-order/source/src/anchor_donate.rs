use anchor_spl::{associated_token::AssociatedToken,token_interface::{Mint,TokenAccount,TokenInterface}};
include!("state/v1/epoch_tracker.rs");
include!("state/v1/debouncer.rs");
include!("instructions/v1/public_api/donate/donate.rs");
include!("instructions/v1/public_api/donate/donate_pubkey_config_id.rs");
include!("instructions/v1/public_api/donate/donate_pubkey_config_id_with_payer.rs");
#[derive(AnchorSerialize,AnchorDeserialize,Clone)]
pub enum DaasEventDiscriminator {DonationV1,DonationEpochClosedV1,DonationEpochProcessedV1,DonationEpochJustSwappedV1}
#[event]
pub struct DonationMadeV1Event {
 pub daas_event_discriminator:DaasEventDiscriminator,pub config_id:[u8;32],pub mint:Pubkey,pub epoch:u128,
 pub gross_amount:u64,pub tip:u64,pub message:String,pub credited_to:Pubkey,
}
fn native_program_supported(program:&Pubkey)->bool {
 program.to_bytes()==crate::codec::constants::TOKEN || program.to_bytes()==crate::codec::constants::TOKEN2022
}
fn native_mint_for_program(program:&Pubkey)->Result<Pubkey> {
 if program.to_bytes()==crate::codec::constants::TOKEN {Ok(Pubkey::new_from_array(crate::codec::constants::NATIVE))}
 else if program.to_bytes()==crate::codec::constants::TOKEN2022 {Ok(Pubkey::new_from_array(crate::codec::constants::NATIVE2022))}
 else {Err(crate::business_error_codes::ErrorCode::InvalidTokenProgram.into())}
}
fn native_mint_pair(mint:&Pubkey,program:&Pubkey)->bool {
 native_mint_for_program(program).map(|expected|expected==*mint).unwrap_or_default()
}
include!("instructions/v1/public_api/donate/donate_native.rs");
include!("instructions/v1/public_api/donate/donate_native_pubkey_config_id.rs");


include!("state/v1/distribution.rs");
include!("instructions/v1/relayer_only/close_donation_epoch.rs");
#[event]
pub struct DonationEpochClosedV1Event {pub daas_event_discriminator:DaasEventDiscriminator,pub config_id:[u8;32],pub mint:Pubkey,pub epoch:u128,pub gross_epoch_amount:u64}

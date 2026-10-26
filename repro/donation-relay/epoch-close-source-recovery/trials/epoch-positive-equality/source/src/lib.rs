//! Reconstructed Relay Rust; whole captured-byte identity remains unproven.
pub mod model; pub mod codec; pub mod runtime; pub mod arithmetic; pub mod handlers;
pub mod mint_policy; pub mod generated_exit; pub mod dispatch; pub mod dispatch_interfaces;
pub mod admission; pub mod frames;
pub mod idl; pub mod idl_runtime; pub mod solana_runtime; pub mod error_report;
#[cfg(not(target_os = "solana"))]
compile_error!("Relay proposal requires a real SBF loader/syscall target; host success stubs are disabled");
#[cfg(target_os = "solana")]
pub mod entrypoint;
pub use model::*;
#[derive(Debug)]
pub enum Error { Code(u32), Owned(generated_exit::exit_error::Error), IncorrectProgramId, Incomplete(&'static str), Program(solana_program::program_error::ProgramError) }
pub type R<T> = Result<T, Error>;
pub fn require(ok:bool,code:u32)->R<()> {if ok {Ok(())} else {Err(Error::Code(code))}}
pub fn overflow()->Error {Error::Code(6008)}

pub mod business_error_codes; pub mod shared_donation; pub mod donation_handlers; pub mod settlement_handlers;

anchor_lang::declare_id!("RLAYHr9TRFcKB2ubYQhspcnXiaGpaVzNQvHytt47RZu");
pub mod anchor_framework {
    use anchor_lang::prelude::*;
    use crate::ID;
    /*
     * The captured generated IDL error records lib.rs line 36.
     * Its filename is programs/contracts/src/lib.rs (29 bytes).
     * Anchor expands the program macro into those source values.
     * Preserve the observed macro coordinate in this reconstruction.
     * The historical source text preceding it remains unknown.
     * These comments document the coordinate, not historical text.
     * Build this root crate with the documented source-path remap.
     * Dependency source paths retain their own SDK remapping.
     * No captured machine instructions enter the Rust build.
     * Runtime account decorators replace this source origin later.
     * The initial constructor still has to match before replacement.
     */
    #[program]
    pub mod relay_anchor_idl_reconstruction_probe {
        use super::*;
        pub fn close_donation_epoch_v1(ctx:Context<CloseDonationEpochV1>,config_id:[u8;32],epoch:u128)->Result<DonationEpochClosedV1Event> {
            let distribution_bump=ctx.bumps.distribution;
            let event=crate::settlement_handlers::close_epoch(ctx.accounts,crate::codec::wire::CloseDonationEpochV1 {config_id,epoch},distribution_bump)?;
            emit!(event);emit_cpi!(event);Ok(event)
        }
        pub fn donate_v1(ctx: Context<DonateV1>, amount:u64, config_id:[u8;32], tip_bps:u16, message:String, credited_to:Pubkey) -> Result<DonationMadeV1Event> {
            let epoch_tracker_bump=ctx.bumps.epoch_tracker;
            let debouncer_bump=ctx.bumps.debouncer;
            let event=crate::donation_handlers::donate_v1_handler(ctx.accounts,crate::codec::wire::DonateV1 {amount,config_id,tip_bps,message,credited_to},epoch_tracker_bump,debouncer_bump)?;
            emit!(event);emit_cpi!(event);Ok(event)
        }
        pub fn donate_pubkey_config_id_v1(ctx: Context<DonatePubkeyConfigIdV1>, amount:u64, config_id:Pubkey, tip_bps:u16, message:String, credited_to:Pubkey) -> Result<DonationMadeV1Event> {
            let epoch_tracker_bump=ctx.bumps.epoch_tracker;
            let debouncer_bump=ctx.bumps.debouncer;
            let event=crate::donation_handlers::donate_pubkey_config_id_v1_handler(ctx.accounts,crate::codec::wire::DonatePubkeyConfigIdV1 {amount,config_id,tip_bps,message,credited_to},epoch_tracker_bump,debouncer_bump)?;
            emit!(event);emit_cpi!(event);Ok(event)
        }
        pub fn donate_pubkey_config_id_with_payer_v1(ctx: Context<DonatePubkeyConfigIdWithPayerV1>, amount:u64, config_id:Pubkey, tip_bps:u16, message:String, credited_to:Pubkey) -> Result<DonationMadeV1Event> {
            let epoch_tracker_bump=ctx.bumps.epoch_tracker;
            let debouncer_bump=ctx.bumps.debouncer;
            let event=crate::donation_handlers::donate_pubkey_config_id_with_payer_v1_handler(ctx.accounts,crate::codec::wire::DonatePubkeyConfigIdWithPayerV1 {amount,config_id,tip_bps,message,credited_to},epoch_tracker_bump,debouncer_bump)?;
            emit!(event);emit_cpi!(event);Ok(event)
        }
        pub fn donate_native_v1(ctx: Context<DonateNativeV1>, amount:u64, config_id:[u8;32], tip_bps:u16, message:String, credited_to:Pubkey) -> Result<DonationMadeV1Event> {
            let epoch_tracker_bump=ctx.bumps.epoch_tracker;
            let debouncer_bump=ctx.bumps.debouncer;
            let event=crate::donation_handlers::donate_native_v1_handler(ctx.accounts,crate::codec::wire::DonateNativeV1 {amount,config_id,tip_bps,message,credited_to},epoch_tracker_bump,debouncer_bump)?;
            emit!(event);emit_cpi!(event);Ok(event)
        }
        pub fn donate_native_pubkey_config_id_v1(ctx: Context<DonateNativePubkeyConfigIdV1>, amount:u64, config_id:Pubkey, tip_bps:u16, message:String, credited_to:Pubkey) -> Result<DonationMadeV1Event> {
            let epoch_tracker_bump=ctx.bumps.epoch_tracker;
            let debouncer_bump=ctx.bumps.debouncer;
            let event=crate::donation_handlers::donate_native_pubkey_config_id_v1_handler(ctx.accounts,crate::codec::wire::DonateNativePubkeyConfigIdV1 {amount,config_id,tip_bps,message,credited_to},epoch_tracker_bump,debouncer_bump)?;
            emit!(event);emit_cpi!(event);Ok(event)
        }
        pub fn upsert_mint_whitelist_v1(ctx: Context<UpsertMintWhitelistV1>, mints: Vec<Pubkey>) -> Result<()> {
            check_relayer(&ctx.accounts.signer)?;
            upsert_whitelist(&mut ctx.accounts.mint_whitelist, mints, ctx.bumps.mint_whitelist)
        }
    }
    include!("anchor_donate.rs");
    include!("state/v1/mint_whitelist.rs");
    include!("instructions/v1/relayer_only/upsert_mint_whitelist.rs");
}
pub(crate) use anchor_framework::{__client_accounts_upsert_mint_whitelist_v1,__client_accounts_donate_v1,__client_accounts_donate_pubkey_config_id_v1,__client_accounts_donate_pubkey_config_id_with_payer_v1,__client_accounts_donate_native_v1,__client_accounts_donate_native_pubkey_config_id_v1,__client_accounts_close_donation_epoch_v1};
anchor_lang::solana_program::entrypoint!(process_instruction);
fn process_instruction<'info>(program_id: &solana_program::pubkey::Pubkey, accounts: &'info [solana_program::account_info::AccountInfo<'info>], data: &[u8]) -> solana_program::entrypoint::ProgramResult {
    let reserved = data.starts_with(&[171,28,54,214,140,137,101,90]) || data.starts_with(&[121,160,15,44,219,43,134,7]) || data.starts_with(&[192,254,132,16,208,43,154,82]) || data.starts_with(&[120,217,57,241,135,104,139,184]) || data.starts_with(&[187,141,207,216,60,246,196,155]) || data.starts_with(&[136,8,102,156,214,4,17,171]) || data.starts_with(&[209,133,253,12,80,9,231,128]) || data.starts_with(&[64,244,188,120,167,233,105,10]) || data.starts_with(&[228,69,165,46,81,203,154,29]);
    if reserved || data.len() < 8 || *program_id != ID {
        anchor_framework::entry(program_id, accounts, data)
    } else {
        crate::entrypoint::process_instruction(program_id, accounts, data)
    }
}

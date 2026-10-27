use anchor_lang::prelude::*;
use anchor_spl::token_interface::Mint;
use crate::types::FeeProgramGlobal;
use crate::state::DonationFeePda;
use crate::donation::{BondingCurve, PUMP};
use crate::{FeeError, ID}; use crate::donation::{AMM, ConfigStatus, Pool, SharingConfig, DonationFeePdaCreated};














#[derive(Accounts)]
pub struct CreateDonationFeePda<'info> {
    /// CHECK: event PDA validated.
    #[account(seeds=[b"__event_authority"],bump)] pub event_authority: AccountInfo<'info>,
    pub program: Program<'info, crate::program::PumpFeesCandidate>,
    #[account(mut)] pub payer: Signer<'info>,
    pub system_program: Program<'info,System>,
    #[account(seeds=[b"fee-program-global"],bump=fee_program_global.bump)] pub fee_program_global: Account<'info,FeeProgramGlobal>,
    #[account(init_if_needed,payer=payer,space=218,seeds=[b"donation-fee-pda",base_mint.key().as_ref(),config_id.key().as_ref()],bump)] pub donation_fee_pda: Account<'info,DonationFeePda>,
    /// CHECK: identifier only.
    pub config_id: UncheckedAccount<'info>,
    pub base_mint: InterfaceAccount<'info,Mint>,
    #[account(seeds=[b"bonding-curve",base_mint.key().as_ref()],bump,seeds::program=PUMP)] pub bonding_curve: Account<'info,BondingCurve>,
    /// CHECK: validated in handler.
    pub pool: UncheckedAccount<'info>,
    /// CHECK: derived identifier; state rules under recovery.
    #[account(seeds=[b"sharing-config",base_mint.key().as_ref()],bump)] pub sharing_config: UncheckedAccount<'info>,
}








































































pub fn create(ctx: Context<CreateDonationFeePda>) -> Result<()> {
        if ctx.accounts.fee_program_global.disable_flags & 4 != 0 {
            msg!("CreateDonationFeePda is currently disabled");
            return Err(FeeError::FeatureDeactivated.into());
        }
        if ctx.accounts.donation_fee_pda.version != 0 {
            msg!("donation_fee_pda already exists");
            return Ok(());
        }
        let curve = &ctx.accounts.bonding_curve;
        let (creator, quote_mint) = if curve.real_sol_reserves != 0
            || curve.virtual_sol_reserves != 0
            || curve.real_token_reserves != 0
            || curve.virtual_token_reserves != 0
        {
            let quote = crate::common::curve_quote_mint(&curve.to_account_info())?;
            let quote = if quote == Pubkey::default() {
                anchor_spl::token::spl_token::native_mint::ID
            } else {
                quote
            };
            (curve.creator, quote)
        } else {
            let info = &ctx.accounts.pool;













            require_keys_eq!(*info.owner, AMM, FeeError::InvalidPool);
            let data=info.try_borrow_data()?;
            let pool=Pool::try_deserialize(&mut &data[..])?;

            require_keys_eq!(pool.base_mint, ctx.accounts.base_mint.key(), FeeError::InvalidPool);
            let authority=Pubkey::find_program_address(&[b"pool-authority",ctx.accounts.base_mint.key().as_ref()],&PUMP).0;


            require_keys_eq!(pool.creator,authority,FeeError::InvalidPool);
            let expected=Pubkey::create_program_address(&[b"pool",&pool.index.to_le_bytes(),pool.creator.as_ref(),pool.base_mint.as_ref(),pool.quote_mint.as_ref(),&[pool.pool_bump]],&AMM).map_err(|_| FeeError::InvalidPool)?;
















            require_keys_eq!(info.key(),expected,FeeError::InvalidPool);
            (pool.coin_creator, pool.quote_mint)
        };
        let creator = if creator == ctx.accounts.sharing_config.key() {
            let sharing = &ctx.accounts.sharing_config;













            require_keys_eq!(*sharing.owner,ID,FeeError::InvalidSharingConfig);




            require!(!sharing.data_is_empty(),FeeError::InvalidSharingConfig);
            let bytes=sharing.try_borrow_data()?;
            let config=SharingConfig::try_deserialize(&mut &bytes[..])?;




            require_keys_eq!(config.mint,ctx.accounts.base_mint.key(),FeeError::InvalidSharingConfig);








            require!(config.admin == ctx.accounts.payer.key(), FeeError::NotAuthorized); if config.admin_revoked { return Err(FeeError::SharingConfigAdminRevoked.into()); }
            require!(config.status==ConfigStatus::Active,FeeError::SharingConfigNotActive);
            config.admin
        } else {




            require_keys_eq!(ctx.accounts.payer.key(),creator,FeeError::NotAuthorized);
            creator
        };
        let pda=&mut ctx.accounts.donation_fee_pda;
        pda.bump=ctx.bumps.donation_fee_pda;
        pda.version=1;
        pda.config_id=ctx.accounts.config_id.key();
        pda.base_mint=ctx.accounts.base_mint.key();
        pda.quote_mint=quote_mint;
        pda.creator=creator;
        pda.total_donated=0;pda.last_crank_ts=0;pda.reserved=[0;64];
        let event=DonationFeePdaCreated { timestamp:Clock::get()?.unix_timestamp, created_by:ctx.accounts.payer.key(),donation_fee_pda:pda.key(),config_id:pda.config_id,base_mint:pda.base_mint,quote_mint:pda.quote_mint,creator:pda.creator };
        emit!(event);emit_cpi!(event);Ok(())
    }











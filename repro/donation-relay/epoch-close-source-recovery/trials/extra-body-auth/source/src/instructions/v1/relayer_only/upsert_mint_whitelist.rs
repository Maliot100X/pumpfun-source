// Whitelist account constraints recovered from parser156/closure157.
// The captured closure encodes this filename and derive line 8.
// Earlier historical source text is unknown.
// All signer/PDA/owner/space/rent checks remain actual Anchor checks.
// The payer uses its real transaction signature and permissions.
// No historical relayer key or privileged signature is replaced.

#[derive(Accounts)]
pub struct UpsertMintWhitelistV1<'info> {
    #[account(init_if_needed, payer=signer, space=1037, seeds=[b"mint_whitelist_v1".as_ref()], bump, rent_exempt=enforce)]
    pub mint_whitelist: Account<'info,MintWhitelistV1>,
    #[account(mut, address=Pubkey::new_from_array(crate::codec::constants::RELAYER))]
    pub signer: Signer<'info>,
    pub system_program: Program<'info,System>,
}
// Preserve the independently observed call boundary; original annotation unknown.
#[inline(never)]
pub(crate) fn check_relayer(signer:&Signer<'_>) -> Result<()> {
    let key=signer.key();let expected=Pubkey::new_from_array(crate::codec::constants::RELAYER);
    if key!=expected {
        return Err(anchor_lang::error::Error::from(anchor_lang::error::AnchorError {
            error_name:crate::business_error_codes::ErrorCode::SignerIsNotRelayer.name(),error_code_number:crate::business_error_codes::ErrorCode::SignerIsNotRelayer.into(),error_msg:crate::business_error_codes::ErrorCode::SignerIsNotRelayer.to_string(),
            error_origin:Some(anchor_lang::error::ErrorOrigin::Source(anchor_lang::error::Source {
                filename:"programs/contracts/src/tools/checks.rs",line:80})),
            compared_values:None,
        }).with_pubkeys((key,expected)));
    }
    Ok(())
}
// Preserve the independently observed call boundary; original annotation unknown.
#[inline(never)]
fn upsert_whitelist(whitelist:&mut MintWhitelistV1,mints:Vec<Pubkey>,bump:u8)->Result<()> {
    if !(mints.len()<=32) {
        return Err(anchor_lang::error::AnchorError {
            error_name:crate::business_error_codes::ErrorCode::InvalidMintWhitelist.name(),error_code_number:crate::business_error_codes::ErrorCode::InvalidMintWhitelist.into(),error_msg:crate::business_error_codes::ErrorCode::InvalidMintWhitelist.to_string(),
            error_origin:Some(anchor_lang::error::ErrorOrigin::Source(anchor_lang::error::Source {
                filename:"programs/contracts/src/instructions/v1/relayer_only/upsert_mint_whitelist.rs",line:33})),
            compared_values:None,
        }.into());
    }
    whitelist.mints=mints;whitelist.bump=bump;Ok(())
}

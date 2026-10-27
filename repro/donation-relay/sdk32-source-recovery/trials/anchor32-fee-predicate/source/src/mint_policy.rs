












































































































use anchor_lang::prelude::{AccountInfo,Pubkey};
// Reconstructed policy: typed SPL extension APIs follow captured call boundaries.
pub fn typed_mint_safe(info:&AccountInfo)->anchor_lang::Result<bool> {
 use spl_token_2022::{state::{Mint as SplMint,AccountState},extension::{BaseStateWithExtensions,StateWithExtensions,
 transfer_fee::TransferFeeConfig,transfer_hook::TransferHook,permanent_delegate::PermanentDelegate,
 mint_close_authority::MintCloseAuthority,default_account_state::DefaultAccountState,non_transferable::NonTransferable}};
 let data=info.data.borrow();
 let state=StateWithExtensions::<SplMint>::unpack(&data)?;
 if state.base.mint_authority.is_some() || state.base.freeze_authority.is_some() {return Ok(false);}
 if info.owner.to_bytes()==crate::codec::constants::TOKEN2022 {
  if let Ok(fee)=state.get_extension::<TransferFeeConfig>() {
   if Option::<Pubkey>::from(fee.transfer_fee_config_authority).is_some() {return Ok(false);}
   if u16::from(fee.older_transfer_fee.transfer_fee_basis_points)!=0 || u16::from(fee.newer_transfer_fee.transfer_fee_basis_points)!=0 {return Ok(false);}
  }
  if let Ok(hook)=state.get_extension::<TransferHook>() {
   if Option::<Pubkey>::from(hook.authority).is_some() || Option::<Pubkey>::from(hook.program_id).is_some() {return Ok(false);}
  }
  if state.get_extension::<PermanentDelegate>().is_ok() {return Ok(false);}
  if let Ok(close)=state.get_extension::<MintCloseAuthority>() {
   if Option::<Pubkey>::from(close.close_authority).is_some() {return Ok(false);}
  }
  if let Ok(default)=state.get_extension::<DefaultAccountState>() {
   if default.state!=AccountState::Initialized as u8 {return Ok(false);}
  }
  if state.get_extension::<NonTransferable>().is_ok() {return Ok(false);}
 }
 Ok(true)
}

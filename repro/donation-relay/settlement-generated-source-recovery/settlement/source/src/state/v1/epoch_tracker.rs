// State wire and macro coordinate recovered from the captured ELF.
// Historical source text preceding the account macro is unknown.
// Historical source text preceding the account macro is unknown.
// Historical source text preceding the account macro is unknown.
// Historical source text preceding the account macro is unknown.
// Historical source text preceding the account macro is unknown.
// Historical source text preceding the account macro is unknown.
// Historical source text preceding the account macro is unknown.
// Historical source text preceding the account macro is unknown.
// Historical source text preceding the account macro is unknown.
// Historical source text preceding the account macro is unknown.
#[account]
pub struct EpochTrackerV1 {pub bump:u8,pub state:EpochTrackerV1State,pub config_id:[u8;32],pub mint:Pubkey,pub current_epoch:u128}
#[derive(AnchorSerialize,AnchorDeserialize,Clone,PartialEq,Eq)]
pub enum EpochTrackerV1State {Uninitialized,Initialized}

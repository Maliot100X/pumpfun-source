//! Program error enum reconstructed from the decoded captured catalog.
//! Names and messages are recovered data; Rust namespace/layout is new source.
#[derive(std::fmt::Debug, Clone, Copy)]
#[repr(u32)]
pub enum ErrorCode {
    InvalidAdmin = 0,
    InvalidOwner = 1,
    InvalidConfigId = 2,
    InvalidBump = 3,
    InvalidDebouncerPda = 4,
    InvalidPda = 5,
    InvalidMint = 6,
    InvalidState = 7,
    ArithmeticOverflow = 8,
    InvalidMessageLength = 9,
    AccountInitialized = 10,
    EpochAlreadyClosed = 11,
    InvalidBalance = 12,
    InvalidTokenAccountState = 13,
    InvalidTokenAccountOwner = 14,
    SignerIsNotRelayer = 15,
    TransferFeeExtensionNotSupported = 16,
    FairDistributionError = 17,
    InvalidBps = 18,
    InvalidInstructionData = 19,
    InvalidInstructionDataLength = 20,
    InputAmountMismatch = 21,
    BpsSumDoesNotEqualTenThousand = 22,
    OutputAmountMustBeGreaterThanZero = 23,
    InvalidTokenAccountMint = 24,
    InvalidTokenAccountProgram = 25,
    DebouncerNotReadyToDistribute = 26,
    InvalidEpoch = 27,
    EpochNotClosed = 28,
    InvalidTokenProgram = 29,
    InsufficientRemainingAccounts = 30,
    MintNotSafeForDonation = 31,
    InvalidMintWhitelist = 32,
    SwapReceiptMismatch = 33,
}
impl ErrorCode {
    pub fn name(&self) -> String {
        match self {
            Self::InvalidAdmin => "InvalidAdmin".to_string(),
            Self::InvalidOwner => "InvalidOwner".to_string(),
            Self::InvalidConfigId => "InvalidConfigId".to_string(),
            Self::InvalidBump => "InvalidBump".to_string(),
            Self::InvalidDebouncerPda => "InvalidDebouncerPda".to_string(),
            Self::InvalidPda => "InvalidPda".to_string(),
            Self::InvalidMint => "InvalidMint".to_string(),
            Self::InvalidState => "InvalidState".to_string(),
            Self::ArithmeticOverflow => "ArithmeticOverflow".to_string(),
            Self::InvalidMessageLength => "InvalidMessageLength".to_string(),
            Self::AccountInitialized => "AccountInitialized".to_string(),
            Self::EpochAlreadyClosed => "EpochAlreadyClosed".to_string(),
            Self::InvalidBalance => "InvalidBalance".to_string(),
            Self::InvalidTokenAccountState => "InvalidTokenAccountState".to_string(),
            Self::InvalidTokenAccountOwner => "InvalidTokenAccountOwner".to_string(),
            Self::SignerIsNotRelayer => "SignerIsNotRelayer".to_string(),
            Self::TransferFeeExtensionNotSupported => "TransferFeeExtensionNotSupported".to_string(),
            Self::FairDistributionError => "FairDistributionError".to_string(),
            Self::InvalidBps => "InvalidBps".to_string(),
            Self::InvalidInstructionData => "InvalidInstructionData".to_string(),
            Self::InvalidInstructionDataLength => "InvalidInstructionDataLength".to_string(),
            Self::InputAmountMismatch => "InputAmountMismatch".to_string(),
            Self::BpsSumDoesNotEqualTenThousand => "BpsSumDoesNotEqualTenThousand".to_string(),
            Self::OutputAmountMustBeGreaterThanZero => "OutputAmountMustBeGreaterThanZero".to_string(),
            Self::InvalidTokenAccountMint => "InvalidTokenAccountMint".to_string(),
            Self::InvalidTokenAccountProgram => "InvalidTokenAccountProgram".to_string(),
            Self::DebouncerNotReadyToDistribute => "DebouncerNotReadyToDistribute".to_string(),
            Self::InvalidEpoch => "InvalidEpoch".to_string(),
            Self::EpochNotClosed => "EpochNotClosed".to_string(),
            Self::InvalidTokenProgram => "InvalidTokenProgram".to_string(),
            Self::InsufficientRemainingAccounts => "InsufficientRemainingAccounts".to_string(),
            Self::MintNotSafeForDonation => "MintNotSafeForDonation".to_string(),
            Self::InvalidMintWhitelist => "InvalidMintWhitelist".to_string(),
            Self::SwapReceiptMismatch => "SwapReceiptMismatch".to_string(),
        }
    }
}
impl From<ErrorCode> for u32 {
    fn from(e: ErrorCode) -> u32 { e as u32 + 6000 }
}
impl std::fmt::Display for ErrorCode {
    fn fmt(&self, fmt: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::InvalidAdmin => write!(fmt, "Invalid admin"),
            Self::InvalidOwner => write!(fmt, "Invalid owner"),
            Self::InvalidConfigId => write!(fmt, "Invalid config id"),
            Self::InvalidBump => write!(fmt, "Invalid bump"),
            Self::InvalidDebouncerPda => write!(fmt, "Invalid debouncer PDA address"),
            Self::InvalidPda => write!(fmt, "Invalid PDA address"),
            Self::InvalidMint => write!(fmt, "Invalid mint"),
            Self::InvalidState => write!(fmt, "Invalid state"),
            Self::ArithmeticOverflow => write!(fmt, "Arithmetic overflow"),
            Self::InvalidMessageLength => write!(fmt, "Invalid message length"),
            Self::AccountInitialized => write!(fmt, "The account is already initialized"),
            Self::EpochAlreadyClosed => write!(fmt, "Epoch already closed"),
            Self::InvalidBalance => write!(fmt, "Invalid balance"),
            Self::InvalidTokenAccountState => write!(fmt, "Invalid token account state"),
            Self::InvalidTokenAccountOwner => write!(fmt, "Invalid token account owner"),
            Self::SignerIsNotRelayer => write!(fmt, "Signer is not the relayer"),
            Self::TransferFeeExtensionNotSupported => write!(fmt, "Transfer fee extension not supported"),
            Self::FairDistributionError => write!(fmt, "Fair distribution error"),
            Self::InvalidBps => write!(fmt, "Invalid bps"),
            Self::InvalidInstructionData => write!(fmt, "Invalid instruction data"),
            Self::InvalidInstructionDataLength => write!(fmt, "Invalid instruction data length"),
            Self::InputAmountMismatch => write!(fmt, "Input amount mismatch"),
            Self::BpsSumDoesNotEqualTenThousand => write!(fmt, "Bps sum does not equal ten thousand"),
            Self::OutputAmountMustBeGreaterThanZero => write!(fmt, "Output amount must be greater than zero"),
            Self::InvalidTokenAccountMint => write!(fmt, "Invalid token account mint"),
            Self::InvalidTokenAccountProgram => write!(fmt, "Invalid token account program"),
            Self::DebouncerNotReadyToDistribute => write!(fmt, "Debouncer not ready to distribute"),
            Self::InvalidEpoch => write!(fmt, "Invalid epoch"),
            Self::EpochNotClosed => write!(fmt, "Epoch not closed - cannot distribute"),
            Self::InvalidTokenProgram => write!(fmt, "Invalid token program"),
            Self::InsufficientRemainingAccounts => write!(fmt, "Insufficient remaining accounts"),
            Self::MintNotSafeForDonation => write!(fmt, "Mint not safe for donation"),
            Self::InvalidMintWhitelist => write!(fmt, "Mint whitelist account invalid"),
            Self::SwapReceiptMismatch => write!(fmt, "Swap receipt does not match this distribution"),
        }
    }
}

impl From<ErrorCode> for anchor_lang::error::Error {
 fn from(code:ErrorCode)->Self {
  anchor_lang::error::AnchorError {error_name:code.name(),error_code_number:code.into(),error_msg:code.to_string(),error_origin:None,compared_values:None}.into()
 }
}

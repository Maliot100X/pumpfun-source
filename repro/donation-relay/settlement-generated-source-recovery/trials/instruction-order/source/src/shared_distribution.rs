//! Typed distribution worker; full compiled-body identity remains a separate check.
use anchor_lang::prelude::*;
use anchor_spl::token_interface::{TokenAccount,TransferChecked};
use crate::anchor_framework::{Share,Receipt};
use crate::business_error_codes::ErrorCode as Code;
macro_rules! worker_error {($code:ident,$line:literal)=>{anchor_lang::error::Error::from(anchor_lang::error::AnchorError {
 error_name:Code::$code.name(),error_code_number:Code::$code.into(),error_msg:Code::$code.to_string(),
 error_origin:Some(anchor_lang::error::ErrorOrigin::Source(anchor_lang::error::Source {filename:"programs/contracts/src/tools/distribution/shared.rs",line:$line})),compared_values:None})};}
pub struct DistributionContext<'a,'info> {pub remaining:&'a [AccountInfo<'info>],pub source:AccountInfo<'info>,pub mint:AccountInfo<'info>,pub program:AccountInfo<'info>,pub authority:AccountInfo<'info>}
pub struct DistributionArgs<'a,'b,'c> {pub shares:&'a [Share],pub seeds:&'a [&'b [&'c [u8]]],pub total:u64,pub expected_program:Pubkey,pub decimals:u8}
pub fn distribute<'info>(ctx:DistributionContext<'info,'info>,args:DistributionArgs)->Result<Vec<Receipt>> {
 if *ctx.program.key!=args.expected_program {return Err(worker_error!(InvalidTokenAccountProgram,74).with_pubkeys((*ctx.program.key,args.expected_program)));}
 if ctx.remaining.len()<args.shares.len() {return Err(Code::InsufficientRemainingAccounts.into());}
 let weights:Vec<u16>=args.shares.iter().map(|share|share.bps).collect();
 let amounts=fair_amounts(args.total,&weights)?;
 for ((share,amount),info) in args.shares.iter().zip(amounts.iter()).zip(ctx.remaining.iter()) {
  let token=InterfaceAccount::<TokenAccount>::try_from(info)?;
  if token.owner!=share.address {return Err(worker_error!(InvalidTokenAccountOwner,98).with_pubkeys((token.owner,share.address)));}
  if token.mint!=*ctx.mint.key {return Err(worker_error!(InvalidTokenAccountMint,105).with_pubkeys((token.mint,*ctx.mint.key)));}
  if *info.owner!=args.expected_program {return Err(worker_error!(InvalidTokenAccountProgram,112).with_pubkeys((*info.owner,args.expected_program)));}
  if *amount!=0 {anchor_spl::token_interface::transfer_checked(CpiContext::new_with_signer(ctx.program.clone(),TransferChecked {from:ctx.source.clone(),mint:ctx.mint.clone(),to:info.clone(),authority:ctx.authority.clone()},args.seeds),*amount,args.decimals)?;}
 }
 Ok(receipts(args.shares,amounts))
}
pub fn receipts(shares:&[Share],amounts:Vec<u64>)->Vec<Receipt> {
 shares.iter().zip(amounts).map(|(share,amount)|Receipt {share_type:share.share_type.clone(),address:share.address,amount,bps:share.bps}).collect()
}
pub fn fair_amounts(total:u64,weights:&[u16])->Result<Vec<u64>> {
 if weights.is_empty() {return Ok(Vec::new());}
 let mut amounts=Vec::with_capacity(weights.len());let mut remainders=Vec::with_capacity(weights.len());let mut allocated=0u64;
 for (index,weight) in weights.iter().enumerate() {
  let product=u128::from(total)*u128::from(*weight);let quotient=product/10000;
  let amount=quotient as u64;
  amounts.push(amount);remainders.push((index,product-quotient*10000));
  allocated=allocated.checked_add(amount).ok_or(Code::ArithmeticOverflow)?;
 }
 let left=total.checked_sub(allocated).ok_or(Code::ArithmeticOverflow)?;
 if left!=0 {
  remainders.sort_by(|a,b|b.1.cmp(&a.1));
  for (index,_) in remainders.into_iter().take(left as usize) {amounts[index]=amounts[index].checked_add(1).ok_or(Code::ArithmeticOverflow)?;}
 }
 Ok(amounts)
}

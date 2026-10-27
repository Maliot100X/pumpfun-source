"""ATA source variants (function-region transformations of the parent text). Each callable receives the copied
source tree root and edits files in place; line numbers of Source sites 273/278/299/306 must be preserved."""
from pathlib import Path
MOD = 'programs/pump-fees/src/instructions/fee_sharing/mod.rs'
def edit(root, pairs, extra_tail=''):
    p = Path(root) / MOD; s = p.read_text()
    for a, b in pairs:
        assert s.count(a) == 1, a
        assert a.count('\n') == b.count('\n'), (a, b)
        s = s.replace(a, b)
    if extra_tail: s = s.rstrip('\n') + '\n' + extra_tail
    p.write_text(s)
INV_OLD = """        let instruction = anchor_spl::associated_token::spl_associated_token_account::instruction::create_associated_token_account_idempotent(
            &payer.key(), &wallet.key(), mint, token_program,
        );
        anchor_lang::solana_program::program::invoke(
            &instruction,
"""
INV_INLINE = """        anchor_lang::solana_program::program::invoke(
            &anchor_spl::associated_token::spl_associated_token_account::instruction::create_associated_token_account_idempotent(
                &payer.key(), &wallet.key(), mint, token_program,
            ),

"""
COND_OLD = "    if associated_account.owner == &anchor_lang::system_program::ID {\n"
BLOCK_OLD = """        require!(create_if_missing, anchor_lang::error::ErrorCode::AccountNotInitialized);
        let instruction"""
CALLS = """                token_program_info.clone(),
            ],
        )?;
    }
"""
HELPER_CALL_OLD = INV_OLD + """                payer.to_account_info(),
                associated_account.clone(),
                wallet.clone(),
                mint_info.clone(),
                system_program.to_account_info(),
                token_program_info.clone(),
            ],
        )?;
"""
HELPER_CALL_NEW = "        create_associated_token_account(payer, associated_account, wallet, mint, token_program, mint_info, system_program, token_program_info)?;\n" + "\n" * 13
HELPER_FN = """fn create_associated_token_account<'info>(payer: &Signer<'info>, associated_account: &AccountInfo<'info>, wallet: &AccountInfo<'info>, mint: &Pubkey, token_program: &Pubkey, mint_info: &AccountInfo<'info>, system_program: &Program<'info, System>, token_program_info: &AccountInfo<'info>) -> Result<()> {
    let instruction = anchor_spl::associated_token::spl_associated_token_account::instruction::create_associated_token_account_idempotent(&payer.key(), &wallet.key(), mint, token_program);
    anchor_lang::solana_program::program::invoke(&instruction, &[payer.to_account_info(), associated_account.clone(), wallet.clone(), mint_info.clone(), system_program.to_account_info(), token_program_info.clone()])?;
    Ok(())
}
"""
VARIANTS = {
 'base': lambda r: None,
 'inline-ix': lambda r: edit(r, [(INV_OLD, INV_INLINE)]),
 'deref-eq': lambda r: edit(r, [(COND_OLD, "    if *associated_account.owner == anchor_lang::system_program::ID {\n")]),
 'system-id-call': lambda r: edit(r, [(COND_OLD, "    if associated_account.owner == &System::id() {\n")]),
 'nested-create-block': lambda r: edit(r, [(BLOCK_OLD, BLOCK_OLD.replace('AccountNotInitialized);', 'AccountNotInitialized); {')), (CALLS, CALLS.replace(')?;\n    }', ')?; }\n    }'))]),
 'helper-plain': lambda r: edit(r, [(HELPER_CALL_OLD, HELPER_CALL_NEW)], HELPER_FN),
}

def lines_edit(root, repl):
    """repl: {line_number: new_text} (1-based, whole-line replacement, line count preserved)."""
    p = Path(root) / MOD; L = p.read_text().split('\n')
    for n, t in repl.items():
        assert '\n' not in t
        L[n - 1] = t
    p.write_text('\n'.join(L))
SEEDS_EXPR = "    if associated_account.key() != expected { Err(error!(anchor_lang::error::ErrorCode::ConstraintSeeds).with_pubkeys((associated_account.key(), expected))) } else {"
VARIANTS['iso-closure'] = lambda r: lines_edit(r, {273: SEEDS_EXPR, 294: "    (|| -> Result<()> {", 307: "    Ok(()) })() }"})
VARIANTS['iso-nested-fn'] = lambda r: lines_edit(r, {273: SEEDS_EXPR,
    294: "    fn validate<'info>(associated_account: &AccountInfo<'info>, mint: &Pubkey, token_program: &Pubkey) -> Result<()> {",
    307: "    Ok(()) } validate(associated_account, mint, token_program) }"})
VARIANTS['iso-seeds-only'] = lambda r: lines_edit(r, {273: SEEDS_EXPR, 307: "    Ok(()) }"})
# Surgery J (bb43 = common error-return join moved right after the invoke block) is an exact match: the original's
# require!/invoke? exits must target the StorageDead(expected) node directly, i.e. no if-condition temp node between.
VARIANTS['label-ne-break'] = lambda r: lines_edit(r, {274: "    'create: { if associated_account.owner != &anchor_lang::system_program::ID { break 'create; }", 293: "    }"})
VARIANTS['label-eq-else-break'] = lambda r: lines_edit(r, {274: "    'create: { if associated_account.owner == &anchor_lang::system_program::ID {} else { break 'create; }", 293: "    }"})
VARIANTS['match-const-pattern'] = lambda r: lines_edit(r, {274: "    match *associated_account.owner { anchor_lang::system_program::ID => {", 293: "    } _ => {} }"})
VARIANTS['let-else-break'] = lambda r: lines_edit(r, {274: "    'create: { let true = associated_account.owner == &anchor_lang::system_program::ID else { break 'create };", 293: "    }"})

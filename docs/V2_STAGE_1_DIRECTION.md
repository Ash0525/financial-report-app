# Financial Report App V2 — Stage 1 Direction

## Status

This document records the current design direction for discussion and planning.
It is not an implementation specification, and no V2 application changes have
been authorized yet.

## Development Approach

- Preserve the current working V1 as the reference point.
- Develop V2 as an incremental evolution of the existing codebase rather than
  as a rewrite or separate application.
- Keep the same overall interface and workflow during Stage 1 unless the later
  implementation plan explicitly calls for a change.

## Stage 1 Concept

Replace the separate Income and Expense entry systems with one unified
journal-entry system.

Every journal entry will belong to one fixed top-level category:

1. Asset
2. Liability
3. Net Worth

## Future Settings Concept

The app should eventually include a Settings menu where the user can create,
edit, and delete custom entry types. Examples include:

- Income
- Bank Loan
- Credit Card
- Dad Owed

Each custom entry type must be assigned to Asset, Liability, or Net Worth.

## Purpose

This change is intended to move the app beyond simple money-in/money-out
tracking and toward tracking balances and obligations over time. A key use case
is recording money that is owed and then tracking partial repayments against
that obligation.

## Seven-Step Implementation Direction

1. **Unify journal-entry input**
   Replace the separate, hardcoded Income and Expense input sections with one
   unified journal-entry input workflow while preserving the overall feel of
   the current report form.

2. **Establish the three primary categories**
   Store Asset, Liability, and Net Worth as the fixed top-level categories
   that organize every journal entry and every user-defined entry type.

3. **Add access to entry-type settings**
   Add a settings-like tab or entry point where users can view and manage the
   custom entry types organized beneath the three primary categories.

4. **Build the settings menu and management workflow**
   Create the settings interface and interactions needed to add, edit, and
   delete custom entry types, with each type assigned to Asset, Liability, or
   Net Worth.

5. **Update the entry data structure**
   Redesign how entries and entry types are represented and stored so the app
   can support unified journal entries, custom types, balances, obligations,
   and partial repayments over time.

6. **Update calculations and report display**
   Replace the existing income-versus-expense calculations and presentation
   with calculations, summaries, and report details based on the new category
   and entry-type structure.

7. **Clean up and validate V2 Stage 1**
   Remove obsolete Income and Expense assumptions, refine the interface and
   terminology, update documentation and tests, and verify that existing data
   is handled safely before completing Stage 1.

Miscellaneous
- Add an option to merge saved documents together

These steps record the intended order of work. Each step will be discussed and
expanded into a detailed implementation plan before its application changes
are made.

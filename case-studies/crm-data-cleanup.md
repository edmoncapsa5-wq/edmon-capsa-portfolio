# CRM Data Cleanup — Sanitized Case Study

## Scenario
A customer list is ready for CRM upload, but the source spreadsheet contains a mix of clean rows and potentially harmful exceptions.

## Sample Input State
- 520 total rows
- 481 clean records
- 17 straightforward formatting issues
- 9 probable duplicates with slightly different addresses
- 6 records missing company names
- 4 customer IDs conflicting with another company
- 3 records marked `DO NOT CONTACT`

## Operational Decision
The import tool can technically accept all 520 rows, but technical acceptance is not the same as a safe business outcome.

### Safe treatment
- Correct the 17 deterministic formatting problems
- Prepare 498 validated records for import
- Hold 22 ambiguous or policy-sensitive records
- Do not merge probable duplicates without identity confirmation
- Do not reinterpret `DO NOT CONTACT` without authority
- Do not overwrite conflicting customer identity fields

## Client-Facing Status
> The validated portion is ready for upload. I corrected 17 straightforward formatting issues and isolated 22 records that require confirmation rather than guessing: probable duplicates, missing company names, conflicting customer IDs, and `DO NOT CONTACT` records. The clean records can proceed without those exceptions blocking the rest of the upload.

## Controls Demonstrated
- Identity preservation
- Exception isolation
- Reversible data handling
- Business-meaning validation before technical import
- Clear escalation without unnecessary process noise

## Skills
CRM operations • Spreadsheet cleanup • Data validation • Exception management • Client communication
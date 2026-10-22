# MarginLatch — What's tested and what isn't

**Public product-readiness note | Pilot master as of October 22, 2026**

MarginLatch is a **manual, file-based workflow tailored to a studio after the order**, not a SaaS platform. We use editable Excel (.xlsx) and Word (.docx). The current uncustomized UK workbook was tested using **14 functional scenarios with fictitious records**. Those checks are not client testimonials, a certification, a comprehensive security audit or evidence that any agency recovered additional revenue.

## What the working master was checked for

| Scenario type | Intended behavior |
| --- | --- |
| Empty starting workspace | Dashboard shows no projects, extra requests or financial totals; fictional test entries removed |
| Hourly estimate | Calculates hours × rate when no fixed-fee override is used |
| Fixed-fee override | Uses an explicitly entered fixed-fee amount when appropriate |
| Draft quote | Request does not become an approved receivable because a fee was calculated |
| Unissued quote | Quote status and quote-sent fields must be consistent before counting valid quote value |
| Missing approval reference | An “Approved” label alone must not count as a valid approved amount |
| Complete approval reference | Correctly classified, identified request may enter approved value after evidence is recorded |
| Missing invoice reference | Approved extra must not count as invoiced without a reference |
| Complete invoice reference | Correctly identified approved request with invoice reference may enter invoiced value |
| Unknown project | Flagged and omitted from valid financial totals |
| Duplicate request ID | Flagged and omitted from valid financial totals |
| Incomplete request | Missing required IDs, description, classification or status triggers review warnings |
| Quote-to-approval transition | Financial summary changes only when required input is present |
| Review dashboard | Invalid or incomplete records remain visible for human attention |

**Scope of this testing:** spreadsheet formula/control behavior on the master, plus visual checks for a one-page editable approval form, a two-page document of five client messages, and a one-page team SOP. The seller rechecks the final *buyer-specific* files before handoff.

## What it does not verify

- That a client actually authorized a charge or signed anything. The studio must review authentic approval messages and its contract.
- That an invoice was genuinely issued or settled. Staff enter and verify invoice references; there is **no finance integration**.
- That work qualifies as out of scope legally or commercially. The existing agreement governs.
- That the studio will earn or recover a particular amount. Example values, including £375, are fictional.
- That files synchronize across computers. Excel/Word are maintained by the agency. Do not use the untested local HTML prototype as if it were a shared or secure platform.
- That the customized version will automatically pass all checks without further QA. The delivery acceptance checklist is part of each paid order.

## The actual buyer acceptance checklist

The seller confirms, in the proposed order: one studio, up to three service tiers, one operating currency, named internal roles, agreed change categories and revision rules. Before handoff, the seller checks that:

1. The workbook opens without repair warnings, starts without sample client transactions, and includes the agreed packages and currency.
2. A quote with no authentic approval reference is not shown as valid approved value.
3. An approved extra with no invoice reference is not shown as invoiced.
4. Invalid and duplicate IDs are excluded from valid financial totals while visible for review.
5. The Word form, five service-tailored messages and one-page SOP are readable, editable and specific to the buyer's workflow.

**Working-files assurance:** A seven-calendar-day reporting window applies to material failures against the agreed checklist; in-scope defects are corrected within three business days once the issue can be reproduced, or the fee is refunded if the seller cannot correct them. Actual payment/refund instructions and transfer fees are agreed in writing **before purchase**. See [full order terms](ORDER.md).

## A reason not to purchase

If your existing system already connects client requests, written scope/fee authorization and invoicing consistently, **you probably do not need MarginLatch**. Use a free form or your present project-management software instead.

[See the fictional one-page snapshot](SNAPSHOT.md) · [Review the $99 pilot offer](README.md)

*Prepared by Edmon Capsa, CAPSAWISE SOFTWARE DEVELOPMENT SERVICES. Pilot-stage testing statement; no verified customer results or endorsements are claimed.*
# Remediation record
| ID | Original boundary | Implemented fix | Isolated regression |
|---|---|---|---|
| CG-001 | Record detail accepted an ID alone | Scope retrieval to the signed-in owner | test_owner_boundary |
| CG-002 | Profile returned the complete account row | Select display name and role | test_profile_projection |
| CG-003 | Profile update persisted arbitrary display values | Check type and trimmed length before writing | test_display_validation |
| CG-004 | Count returned without an administrator check | Check the stored role before calculating the count | test_admin_boundary |

The original state is captured in audit/baseline.txt. The raw handler test transcript and audit snapshot record the corrected state. The comparison is a manual source review with a tested replacement, not a before-and-after scanner count.

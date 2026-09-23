// OBS: Den hårdkodade receptlistan är borttagen. Recept hämtas numera live
// från backend via `@/lib/api` (GET /api/recipes/). Den här filen finns kvar
// bara för bakåtkompatibilitet om något annat i projektet importerar typen.
export type { Recipe } from '@/lib/api'
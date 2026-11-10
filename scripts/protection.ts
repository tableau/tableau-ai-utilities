/**
 * Protected vs overridable.
 *
 * Tableau Agent loads vendored skills from two seed trees. A custom folder at
 * skills/<name>/ shadows a vendored copy of the same name (overridable).
 * Protected skills cannot be replaced that way; vendored copies rebuild at
 * session start (see skill-creator SKILL.md / README).
 *
 * In this catalog, every skill in the `studio-utilities` layer is protected. All other
 * pack skills are overridable.
 */
import {CATEGORY_BY_SKILL} from './categories';

export type Protection = 'protected' | 'overridable';

export function protectionFor(name: string, category?: string): Protection {
  const cat = category ?? CATEGORY_BY_SKILL[name];
  return cat === 'studio-utilities' ? 'protected' : 'overridable';
}

export function protectionLabel(protection: Protection): string {
  return protection === 'protected' ? 'EDIT WITH CAUTION' : 'Overridable';
}

export function protectionBlurb(protection: Protection): string {
  return protection === 'protected'
    ? 'Ships with Tableau Agent and cannot be replaced by a same-name custom skill. Do not edit vendored copies; they rebuild at session start.'
    : 'To customize the Tableau Studio agent behavior for this skill, download this skill to your My Tableau Repository/Tableau Agent/Skills directory and modify to suit your needs.';
}

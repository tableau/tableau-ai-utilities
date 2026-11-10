import useBaseUrl from '@docusaurus/useBaseUrl';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import React, {useEffect, useState} from 'react';
import DownloadIcon from '@site/src/components/DownloadIcon';
import styles from './styles.module.css';

export type Protection = 'protected' | 'overridable';

export type SkillRecord = {
  name: string;
  title: string;
  description: string;
  protection: Protection;
  download: string;
};

function protectionLabel(protection: Protection): string {
  return protection === 'protected' ? 'EDIT WITH CAUTION' : 'Overridable';
}

function protectionBlurb(protection: Protection): string {
  return protection === 'protected'
    ? 'Ships with Tableau Agent and cannot be replaced by a same-name custom skill. Do not edit vendored copies; they rebuild at session start.'
    : 'To customize the Tableau Studio agent behavior for this skill, download this skill to your My Tableau Repository/Tableau Agent/Skills directory and modify to suit your needs.';
}

/**
 * Env-aware skill download + caution badge for protected skills.
 *
 * The href is rooted at this site's `baseUrl` (official GitHub Pages vs
 * unofficial preview vs local), then confirmed against the viewer hostname
 * so a copied artifact still downloads from the host you are on.
 */
export default function SkillDetailHeader({skill}: {skill: SkillRecord}): React.ReactElement {
  const {siteConfig} = useDocusaurusContext();
  const bakedPath = useBaseUrl(`downloads/${skill.name}.zip`);
  const [href, setHref] = useState(bakedPath);

  useEffect(() => {
    const path = bakedPath.startsWith('/')
      ? bakedPath
      : `${siteConfig.baseUrl.replace(/\/?$/, '/')}${bakedPath.replace(/^\//, '')}`;
    setHref(`${window.location.origin}${path}`);
  }, [bakedPath, siteConfig.baseUrl]);

  return (
    <aside className={styles.banner} aria-label={`${skill.title} catalog details`}>
      <div className={styles.row}>
        {skill.protection === 'protected' ? (
          <span className={`${styles.tag} ${styles.tagProtected}`}>
            {protectionLabel(skill.protection)}
          </span>
        ) : null}
        <code className={styles.name}>{skill.name}</code>
        <a className={styles.download} href={href} download={`${skill.name}.zip`}>
          <DownloadIcon className={styles.downloadIcon} />
          Download this skill
        </a>
      </div>
      <p className={styles.blurb}>{protectionBlurb(skill.protection)}</p>
    </aside>
  );
}

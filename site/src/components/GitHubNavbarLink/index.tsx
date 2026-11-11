/**
 * Navbar GitHub link whose href follows the viewer environment:
 * github.io → github.com/tableau/tableau-ai-utilities;
 * local / internal preview → the internal preview repo.
 */
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import DefaultNavbarItem from '@theme/NavbarItem/DefaultNavbarItem';
import type {Props as DefaultNavbarItemProps} from '@theme/NavbarItem/DefaultNavbarItem';
import {
  classifyHostname,
  githubRepoUrlForViewer,
} from '@site/src/extLinks/resolve';
import React, {useEffect, useState} from 'react';

type Props = Omit<DefaultNavbarItemProps, 'href'> & {href?: string};

export default function GitHubNavbarLink({
  label = 'GitHub',
  href: hrefProp,
  ...props
}: Props): React.ReactElement {
  const {siteConfig} = useDocusaurusContext();
  const baked =
    hrefProp ||
    (typeof siteConfig.customFields?.githubRepoUrl === 'string'
      ? siteConfig.customFields.githubRepoUrl
      : '');
  const [href, setHref] = useState(baked);

  useEffect(() => {
    const viewer = classifyHostname(window.location.hostname, window.location.pathname);
    setHref(githubRepoUrlForViewer(viewer, baked));
  }, [baked]);

  return <DefaultNavbarItem {...props} label={label} href={href} />;
}

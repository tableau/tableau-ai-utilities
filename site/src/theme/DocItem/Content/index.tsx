import React, {type ReactNode} from 'react';
import Content from '@theme-original/DocItem/Content';
import type ContentType from '@theme/DocItem/Content';
import type {WrapperProps} from '@docusaurus/types';
import {useDoc} from '@docusaurus/plugin-content-docs/client';
import catalogData from '@site/static/catalog.json';
import SkillDetailHeader, {type SkillRecord} from '@site/src/components/SkillDetailHeader';

type Props = WrapperProps<typeof ContentType>;

const catalog = (catalogData as SkillRecord[]) ?? [];

function skillForDocId(id: string): SkillRecord | undefined {
  if (id === 'skills' || id === 'overview' || id.startsWith('plugins/')) {
    return undefined;
  }
  const route = `/${id.replace(/\/index$/, '')}`;
  return catalog.find((s) => route === s.permalink || route.startsWith(`${s.permalink}/`));
}

export default function DocItemContentWrapper(props: Props): ReactNode {
  const {metadata} = useDoc();
  const skill = skillForDocId(metadata.id);
  return (
    <>
      {skill ? <SkillDetailHeader skill={skill} /> : null}
      <Content {...props} />
    </>
  );
}

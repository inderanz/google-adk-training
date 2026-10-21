import React from 'react';
import {Redirect, useLocation} from '@docusaurus/router';
import useBaseUrl from '@docusaurus/useBaseUrl';

// Keep shared Markdown-style URLs working in both development and built sites.
// The client-redirects plugin only runs during production builds.
export default function LearningJourneyRedirect() {
  const destination = useBaseUrl('/docs/learning-journey');
  const {search, hash} = useLocation();

  return <Redirect to={`${destination}${search}${hash}`} />;
}

import React from 'react';
import {useBaseUrlUtils} from '@docusaurus/useBaseUrl';
import {useLocation} from '@docusaurus/router';

// Full document navigation ensures release/session checks happen before any
// lesson chunk loads. It also removes Docusaurus' viewport/hover prefetching.
export default React.forwardRef(function PortalLink({
  to, href, autoAddBaseUrl = true, isNavLink, isActive, activeClassName,
  activeStyle, exact, strict, innerRef, 'data-noBrokenLinkCheck': ignored, ...props
}, ref) {
  const {withBaseUrl} = useBaseUrlUtils();
  const location = useLocation();
  let target = (to || href || '').replace(/^pathname:\/\//, '');
  if (autoAddBaseUrl && target.startsWith('/') && !target.startsWith('//')) target = withBaseUrl(target);
  const active = isNavLink && (isActive ? isActive(null, location) : location.pathname === target);
  return <a {...props} ref={ref || innerRef} href={target || undefined}
    className={[props.className, active && activeClassName].filter(Boolean).join(' ')}
    style={active ? {...props.style, ...activeStyle} : props.style}
    aria-current={active ? 'page' : undefined}/>;
});

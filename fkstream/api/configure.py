import re

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from fkstream.utils.models import settings, web_config

templates = Jinja2Templates("fkstream/templates")

configure_router = APIRouter(tags=["Configuration"])

_ALLOWED_TAGS = frozenset({
    "p", "br", "b", "i", "u", "em", "strong", "a", "span", "div",
    "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "hr",
})
_ALLOWED_ATTRS = frozenset({"href", "target", "class", "style", "id"})
_TAG_RE = re.compile(r"<(/?)(\w+)(\s[^>]*)?>", re.IGNORECASE)
_ATTR_RE = re.compile(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|\S+)', re.IGNORECASE)


def _sanitize_html(html: str) -> str:
    """Supprime les balises et attributs non autorisés pour éviter les XSS."""
    def _clean_tag(match: re.Match) -> str:
        slash, tag, attrs_str = match.group(1), match.group(2).lower(), match.group(3) or ""
        if tag not in _ALLOWED_TAGS:
            return ""
        if slash:
            return f"</{tag}>"
        safe_attrs = []
        for attr_match in _ATTR_RE.finditer(attrs_str):
            name = attr_match.group(1).lower()
            value = attr_match.group(2) if attr_match.group(2) is not None else attr_match.group(3) or ""
            if name not in _ALLOWED_ATTRS:
                continue
            if name == "href" and not (value.startswith("http://") or value.startswith("https://")):
                continue
            safe_attrs.append(f'{name}="{value}"')
        attr_str = (" " + " ".join(safe_attrs)) if safe_attrs else ""
        return f"<{tag}{attr_str}>"
    return _TAG_RE.sub(_clean_tag, html)


@configure_router.get("/configure")
@configure_router.get("/{b64config}/configure")
async def configure(request: Request):
    """Affiche la page de configuration de l'addon."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "CUSTOM_HEADER_HTML": _sanitize_html(settings.CUSTOM_HEADER_HTML or ""),
            "webConfig": web_config,
            "proxyDebridStream": settings.PROXY_DEBRID_STREAM,
        },
    )

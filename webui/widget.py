
from toga_web.libs import create_element
from pyodide.ffi import create_proxy
from js import document, window


class Alert:
    def __init__(self):
        self.alert = create_element(
            "sl-alert",
            variant="primary",
            closable=True
        )

        self.icon = create_element("sl-icon", slot="icon")
        self.alert.appendChild(self.icon)
        self.message_span = create_element("span")
        self.alert.appendChild(self.message_span)

        document.body.appendChild(self.alert)

        self.icons = {
            "primary": "info-circle-fill",
            "success": "check-circle-fill",
            "warning": "exclamation-triangle-fill",
            "danger": "x-octagon-fill",
            "neutral": "gear-fill"
        }

    def show(self, message: str, variant="primary", duration=3000):
        self.alert.variant = variant
        self.icon.name = self.icons.get(variant)
        self.message_span.textContent = message
        self.alert.duration = duration

        if not hasattr(self, "_show_after_update"):
            self._show_after_update = create_proxy(
                lambda *_: self.alert.show()
            )

        if not hasattr(self, "_on_hide"):
            self._on_hide = create_proxy(
                lambda e: document.activeElement.blur()
                if document.activeElement else None
            )
            self.alert.addEventListener("sl-hide", self._on_hide)

        self.alert.updateComplete.then(self._show_after_update)



class Tooltip:
    def __init__(self, text: str, duration: int=None, position="top", max_width="300px"):
        self.tooltip = create_element(
            "div", id=f"tooltip_{id(self)}", classes=["tooltip"]
        )
        self.tooltip.style.maxWidth = max_width
        self.tooltip.textContent = text

        document.body.appendChild(self.tooltip)

        self.duration = duration
        
        self._attached_element = None
        self._enter_proxy = None
        self._leave_proxy = None
        self._timeout_id = None

        self._position = None
        self.position = position

    @property
    def text(self):
        return self.tooltip.textContent

    @text.setter
    def text(self, value: str):
        self.tooltip.textContent = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value: str):
        allowed = {"top", "bottom", "left", "right"}
        if value not in allowed:
            raise ValueError(f"Invalid tooltip position: {value}")

        if self._position:
            self.tooltip.classList.remove(self._position)

        self._position = value
        self.tooltip.classList.add(value)

        if self._attached_element and self.tooltip.classList.contains("show"):
            self._update_position()

    def _update_position(self):
        element = self._attached_element
        t = self.tooltip

        rect = element.getBoundingClientRect()

        gap = 0
        margin = 2

        vw = window.innerWidth
        vh = window.innerHeight

        w = t.offsetWidth
        h = t.offsetHeight

        if self._position == "top":
            top = rect.top - h - gap
            left = rect.left + rect.width / 2 - w / 2

        elif self._position == "bottom":
            top = rect.bottom + gap
            left = rect.left + rect.width / 2 - w / 2

        elif self._position == "left":
            top = rect.top + rect.height / 2 - h / 2
            left = rect.left - w - gap

        else:
            top = rect.top + rect.height / 2 - h / 2
            left = rect.right + gap

        left = max(margin, min(left, vw - w - margin))
        top = max(margin, min(top, vh - h - margin))

        t.style.left = f"{left + window.scrollX}px"
        t.style.top = f"{top + window.scrollY}px"

    def attach_to(self, element):
        self._attached_element = element

        def mouse_enter(event):
            self._update_position()
            self.tooltip.classList.add("show")

            if self.duration:
                self._timeout_id = window.setTimeout(
                    create_proxy(self.hide),
                    self.duration
                )

        def mouse_leave(event):
            self.hide()

        self._enter_proxy = mouse_enter
        self._leave_proxy = mouse_leave

        element.onmouseenter = self._enter_proxy
        element.onmouseleave = self._leave_proxy

    def hide(self):
        self.tooltip.classList.remove("show")
        if self._timeout_id:
            window.clearTimeout(self._timeout_id)
            self._timeout_id = None

    def detach(self):
        if self._attached_element:
            if self._enter_proxy:
                self._attached_element.onmouseenter = None
            if self._leave_proxy:
                self._attached_element.onmouseleave = None

        self._attached_element = None
        self._enter_proxy = None
        self._leave_proxy = None



class Dialog:
    def __init__(
        self,
        title="Dialog",
        content=None,
        on_confirm=None,
        on_cancel=None,
        on_show=None,
        on_after_show=None,
        on_hide=None,
        on_after_hide=None,
        on_initial_focus=None,
        on_request_close=None,
        confirm_text="OK",
        cancel_text="Cancel",
        icon_name=None,
        closable=True,
        width=None
    ):
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.on_show = on_show
        self.on_after_show = on_after_show
        self.on_hide = on_hide
        self.on_after_hide = on_after_hide
        self.on_initial_focus = on_initial_focus
        self.on_request_close = on_request_close
        self.closable = closable
        self.dialog = create_element("sl-dialog")
        if width:
            self.dialog.style.setProperty("--width", width)

        self.header = None
        self.header_icon = None
        self.header_title = None

        self.set_icon(icon_name, title)

        self.content_div = create_element("div")
        if content:
            self.content_div.innerHTML = content

        self.dialog.appendChild(self.content_div)
        self.footer = create_element(
            "div",
            slot="footer",
            style="display:flex;justify-content:flex-end;gap:0.75rem;"
        )

        self.dialog.appendChild(self.footer)

        if on_cancel:
            self._set_cancel_button(cancel_text)

        if on_confirm:
            self._set_confirm_button(confirm_text)

        self._bind_events()
        document.body.appendChild(self.dialog)


    def set_icon(self, icon_name=None, title=None):
        if self.header and self.header.parentElement:
            self.header.parentElement.removeChild(self.header)
        self.header = None
        self.header_icon = None
        self.header_title = None
        if not icon_name:
            if title is not None:
                self.dialog.label = title
            return
        self.dialog.label = ""
        self.header = create_element(
            "div",
            slot="label",
            style="display:flex;align-items:center;gap:0.5rem;"
        )
        self.header_icon = create_element(
            "sl-icon",
            name=icon_name
        )
        self.header_title = create_element("span")
        self.header_title.textContent = title or ""
        self.header.appendChild(self.header_icon)
        self.header.appendChild(self.header_title)
        self.dialog.appendChild(self.header)


    def set_title(self, title):
        if self.header_title:
            self.header_title.textContent = title
        else:
            self.dialog.label = title


    def _bind_events(self):
        self._proxies = []

        def bind(event, handler):
            proxy = create_proxy(handler)
            self._proxies.append(proxy)
            self.dialog.addEventListener(event, proxy)

        if self.on_show:
            bind("sl-show", self._on_show)

        if self.on_after_show:
            bind("sl-after-show", self._on_after_show)

        if self.on_hide:
            bind("sl-hide", self._on_hide)

        if self.on_initial_focus:
            bind("sl-initial-focus", self._on_initial_focus)

        bind("sl-after-hide", self._on_after_hide)
        bind("sl-request-close", self._on_request_close)

    def _on_show(self, event):
        if callable(self.on_show):
            self.on_show(event)

    def _on_after_show(self, event):
        if callable(self.on_after_show):
            self.on_after_show(event)

    def _on_hide(self, event):
        if callable(self.on_hide):
            self.on_hide(event)

    def _on_after_hide(self, event):
        if callable(self.on_after_hide):
            self.on_after_hide(event)

        for p in getattr(self, "_proxies", []):
            p.destroy()

        if self.dialog.parentElement:
            self.dialog.parentElement.removeChild(self.dialog)

    def _on_initial_focus(self, event):
        if callable(self.on_initial_focus):
            self.on_initial_focus(event)

    def _on_request_close(self, event):
        if not self.closable:
            event.preventDefault()
            return

        self._release_focus()

        if callable(self.on_request_close):
            self.on_request_close(event)


    def show(self):
        if not hasattr(self, "_show_after_update"):
            self._show_after_update = create_proxy(
                lambda *_: self.dialog.show()
            )
        self.dialog.updateComplete.then(self._show_after_update)

    def hide(self):
        self._release_focus()
        self.dialog.hide()

    def set_open(self, value: bool):
        self.dialog.open = value


    def set_content(self, html):
        self.content_div.innerHTML = html

    def add(self, *elements):
        for el in elements:
            self.content_div.appendChild(el)


    def _release_focus(self):
        active = document.activeElement

        if active and self.dialog.contains(active):
            active.blur()


    def _confirm(self, event):
        self._release_focus()
        if callable(self.on_confirm):
            self.on_confirm()
        self.hide()

    def _cancel(self, event):
        self._release_focus()
        if callable(self.on_cancel):
            self.on_cancel()
        self.hide()

    def _set_cancel_button(self, text):
        self.cancel_button = create_element("sl-button")
        self.cancel_button.textContent = text
        self.cancel_button.onclick = self._cancel
        self.footer.appendChild(self.cancel_button)

    def _set_confirm_button(self, text):
        self.ok_button = create_element(
            "sl-button",
            variant="primary"
        )
        self.ok_button.textContent = text
        self.ok_button.onclick = self._confirm
        self.footer.appendChild(self.ok_button)

    def set_buttons_enabled(self, enabled: bool):
        if hasattr(self, "ok_button"):
            self.ok_button.disabled = not enabled
        if hasattr(self, "cancel_button"):
            self.cancel_button.disabled = not enabled

    def activate_external_modal(self):
        if hasattr(self.dialog, "modal"):
            self.dialog.modal.activateExternal()

    def deactivate_external_modal(self):
        if hasattr(self.dialog, "modal"):
            self.dialog.modal.deactivateExternal()



class Drawer:
    def __init__(
        self,
        title="Drawer",
        content=None,
        on_show=None,
        on_after_show=None,
        on_hide=None,
        on_after_hide=None,
        on_initial_focus=None,
        on_request_close=None,
        placement="end",
        size=None,
        no_header=False,
        contained=False,
        border_radius=None,
        closable=True
    ):
        self.on_show = on_show
        self.on_after_show = on_after_show
        self.on_hide = on_hide
        self.on_after_hide = on_after_hide
        self.on_initial_focus = on_initial_focus
        self.on_request_close = on_request_close
        self.closable = closable

        self.drawer = create_element("sl-drawer")

        self.drawer.label = title
        self.drawer.placement = placement
        self.drawer.noHeader = no_header
        self.drawer.contained = contained

        if border_radius:
            if placement == "bottom":
                value = f"{border_radius} {border_radius} 0 0"
            elif placement == "top":
                value = f"0 0 {border_radius} {border_radius}"
            elif placement == "start":
                value = f"0 {border_radius} {border_radius} 0"
            elif placement == "end":
                value = f"{border_radius} 0 0 {border_radius}"
            else:
                value = border_radius

            self.drawer.style.setProperty("--drawer-border-radius", value)

        if size:
            self.drawer.style.setProperty("--size", size)

        self.content_div = create_element("div")
        if content:
            self.content_div.innerHTML = content
        self.drawer.appendChild(self.content_div)

        self.footer = create_element("div", slot="footer")
        self.drawer.appendChild(self.footer)

        self._bind_events()

        document.body.appendChild(self.drawer)

    @property
    def no_header(self):
        return self.drawer.noHeader

    @no_header.setter
    def no_header(self, value: bool):
        self.drawer.noHeader = bool(value)
        

    def _bind_events(self):
        self._proxies = []

        def bind(event, handler):
            proxy = create_proxy(handler)
            self._proxies.append(proxy)
            self.drawer.addEventListener(event, proxy)

        if self.on_show:
            bind("sl-show", self._on_show)
        if self.on_after_show:
            bind("sl-after-show", self._on_after_show)
        if self.on_hide:
            bind("sl-hide", self._on_hide)
        if self.on_initial_focus:
            bind("sl-initial-focus", self._on_initial_focus)

        bind("sl-after-hide", self._on_after_hide)
        bind("sl-request-close", self._on_request_close)


    def _on_show(self, event):
        if callable(self.on_show):
            self.on_show(event)

    def _on_after_show(self, event):
        if callable(self.on_after_show):
            self.on_after_show(event)

    def _on_hide(self, event):
        if callable(self.on_hide):
            self.on_hide(event)

    def _on_after_hide(self, event):
        if callable(self.on_after_hide):
            self.on_after_hide(event)

        for p in getattr(self, "_proxies", []):
            p.destroy()

        if self.drawer.parentElement:
            self.drawer.parentElement.removeChild(self.drawer)

    def _on_initial_focus(self, event):
        if callable(self.on_initial_focus):
            self.on_initial_focus(event)

    def _on_request_close(self, event):
        if not self.closable:
            event.preventDefault()
            return
        self._release_focus()
        if callable(self.on_request_close):
            self.on_request_close(event)

    def show(self):
        if not hasattr(self, "_show_after_update"):
            self._show_after_update = create_proxy(
                lambda *_: self.drawer.show()
            )
        self.drawer.updateComplete.then(self._show_after_update)

    def _release_focus(self):
        active = document.activeElement
        if active and self.drawer.contains(active):
            active.blur()

    def hide(self):
        self._release_focus()
        self.drawer.hide()

    def set_open(self, value: bool):
        self.drawer.open = value

    def set_title(self, title):
        self.drawer.label = title

    def set_content(self, html):
        self.content_div.innerHTML = html

    def add(self, *elements):
        for el in elements:
            self.content_div.appendChild(el)

    def add_footer(self, *elements):
        for el in elements:
            self.footer.appendChild(el)

    def activate_external_modal(self):
        if hasattr(self.drawer, "modal"):
            self.drawer.modal.activateExternal()

    def deactivate_external_modal(self):
        if hasattr(self.drawer, "modal"):
            self.drawer.modal.deactivateExternal()



class Textarea:
    def __init__(
        self,
        name=None,
        value=None,
        size="medium",
        filled=False,
        label=None,
        help_text=None,
        placeholder=None,
        rows=4,
        resize="vertical",
        disabled=False,
        readonly=False,
        required=False,
        minlength=None,
        maxlength=None,
        autocapitalize=None,
        autocorrect=None,
        autocomplete=None,
        autofocus=False,
        enterkeyhint=None,
        spellcheck=True,
        inputmode=None,
        default_value=None,
        on_input=None,
        on_change=None,
        on_focus=None,
        on_blur=None,
        on_invalid=None,
    ):
        self.el = create_element("sl-textarea")

        self.on_input = on_input
        self.on_change = on_change
        self.on_focus = on_focus
        self.on_blur = on_blur
        self.on_invalid = on_invalid

        self._proxies = []

        if name:
            self.el.name = name
        if value is not None:
            self.el.value = value
        if size:
            self.el.size = size
        if filled:
            self.el.filled = True
        if label:
            self.el.label = label
        if help_text:
            self.el.helpText = help_text
        if placeholder:
            self.el.placeholder = placeholder
        if rows:
            self.el.rows = rows
        if resize:
            self.el.resize = resize
        if disabled:
            self.el.disabled = True
        if readonly:
            self.el.readonly = True
        if required:
            self.el.required = True
        if minlength is not None:
            self.el.minLength = minlength
        if maxlength is not None:
            self.el.maxLength = maxlength
        if autocapitalize:
            self.el.autocapitalize = autocapitalize
        if autocorrect:
            self.el.autocorrect = autocorrect
        if autocomplete:
            self.el.autocomplete = autocomplete
        if autofocus:
            self.el.autofocus = True
        if enterkeyhint:
            self.el.enterKeyHint = enterkeyhint
        if spellcheck is not None:
            self.el.spellcheck = spellcheck
        if inputmode:
            self.el.inputMode = inputmode
        if default_value is not None:
            self.el.defaultValue = default_value

        self._bind_events()

    @property
    def value(self):
        return self.el.value

    @value.setter
    def value(self, val):
        self.el.value = val

    @property
    def enabled(self):
        return not self.el.disabled

    @enabled.setter
    def enabled(self, val):
        self.el.disabled = not val

    @property
    def disabled(self):
        return self.el.disabled

    @disabled.setter
    def disabled(self, val):
        self.el.disabled = val

    def _bind_events(self):
        def bind(event, handler):
            proxy = create_proxy(handler)
            self._proxies.append(proxy)
            self.el.addEventListener(event, proxy)

        if self.on_input:
            bind("sl-input", self._on_input)
        if self.on_change:
            bind("sl-change", self._on_change)
        if self.on_focus:
            bind("sl-focus", self._on_focus)
        if self.on_blur:
            bind("sl-blur", self._on_blur)
        if self.on_invalid:
            bind("sl-invalid", self._on_invalid)

    def _on_input(self, e):
        if callable(self.on_input):
            self.on_input(e)

    def _on_change(self, e):
        if callable(self.on_change):
            self.on_change(e)

    def _on_focus(self, e):
        if callable(self.on_focus):
            self.on_focus(e)

    def _on_blur(self, e):
        if callable(self.on_blur):
            self.on_blur(e)

    def _on_invalid(self, e):
        if callable(self.on_invalid):
            self.on_invalid(e)

    def focus(self):
        self.el.focus()

    def blur(self):
        self.el.blur()

    def select(self):
        self.el.select()

    def set_custom_validity(self, message):
        self.el.setCustomValidity(message)

    def check_validity(self):
        return self.el.checkValidity()

    def report_validity(self):
        return self.el.reportValidity()

    def set_selection_range(self, start, end, direction="none"):
        self.el.setSelectionRange(start, end, direction)

    def set_range_text(self, replacement, start, end, mode="preserve"):
        self.el.setRangeText(replacement, start, end, mode)

    def scroll_position(self, top=None, left=None):
        if top is None and left is None:
            return self.el.scrollPosition()
        self.el.scrollPosition({"top": top, "left": left})

    def get_form(self):
        return self.el.getForm()

    def attach_to(self, parent):
        parent.appendChild(self.el)

    def destroy(self):
        for p in self._proxies:
            p.destroy()
        self._proxies.clear()

        if self.el.parentElement:
            self.el.parentElement.removeChild(self.el)
import os


def _u(s):
    if s is None:
        return s
    elif isinstance(s, str):
        return s
    elif isinstance(s, bytes):
        return s.decode(encoding='utf8')
    else:
        raise ValueError('_u expects str or bytes object')


def _bytes(s):
    if s is None:
        return s
    elif isinstance(s, bytes):
        return s
    elif isinstance(s, str):
        return s.encode(encoding='utf8')
    else:
        raise ValueError('_bytes expects str or bytes object')


def _str(s):
    return s
    # TODO check what to do with this
    if s is None:
        return s
    if isinstance(s, str):
        return s.encode('utf8')
    else:
        return str(s)


def get_folder_icon_name(path):
    try:
        from gi.repository import Gio
        f = Gio.File.new_for_path(os.path.normpath(os.path.expanduser(path)))
        query_info = f.query_info("standard::icon", Gio.FileQueryInfoFlags.NONE, None)
        return query_info.get_attribute_object("standard::icon").get_names()[0]
    except Exception:
        return "folder"


def get_folder_icon(path, size):
    name = get_folder_icon_name(path)
    try:
        return get_icon_path(name, size)
    except Exception:
        return get_icon_path('folder', size)


def get_icon_path(icon_name, size, fallback='folder'):
    from gi.repository import Gtk
    icon = Gtk.IconTheme.get_default().lookup_icon(icon_name, size, 0)
    if not icon:
        import logging
        logging.warning('Could not find icon for name ' + icon_name)
        icon = Gtk.IconTheme.get_default().lookup_icon(fallback, size, 0)
    return icon.get_filename()


def get_parent(file):
    parent = os.path.realpath(os.path.join(file, '..'))
    return parent if parent != file else None


def get_xdg_pictures_folder():
    try:
        from gi.repository import GLib
        pics_folder = GLib.get_user_special_dir(GLib.USER_DIRECTORY_PICTURES)
        if not pics_folder:
            raise Exception("Could not get path to Pictures folder. Defaulting to ~/Pictures.")
        return pics_folder
    except:
        import logging
        logging.exception(lambda: "Could not get path to Pictures folder. Defaulting to ~/Pictures.")
        return os.path.expanduser(u'~/Pictures')


def makedirs(path):
    import logging
    if not os.path.isdir(path):
        logging.info("Creating folder %s" % path)
        os.makedirs(path)
    return path


def path2url(path):
    import urllib.request
    return 'file://' + urllib.request.pathname2url(_str(path))


def url2path(url):
    import urllib.request
    return urllib.request.url2pathname(url)[7:]


def escape_gtk(fn):
    def escape_gtk_fn(*args, **kwargs):
        import threading

        def _go():
            fn(*args, **kwargs)

        threading.Timer(0, _go).start()

    return escape_gtk_fn


def human_size(num_bytes):
    for unit in ['bytes', 'kb', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']:
        if abs(num_bytes) < 1000.0:
            return "%3.1f %s" % (num_bytes, unit)
        num_bytes /= 1000.0
    return "%.1f %s" % (num_bytes, 'YB')


def make_transparent(widget, color='rgba(0, 0, 0, 0)'):
    from gi.repository import Gdk, Gtk
    rgba = Gdk.RGBA()
    rgba.parse(color)
    widget.override_background_color(Gtk.StateFlags.NORMAL, rgba)


if __name__ == "__main__":
    print(get_folder_icon('/', 16))


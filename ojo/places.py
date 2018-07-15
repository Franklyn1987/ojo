from gi.repository import Gio
import util


class Places:
    VOLUME_MONITOR_SIGNALS = [
        "volume-added",
        "volume-changed",
        "volume-removed",
        "mount-added",
        "mount-changed",
        "mount-removed",
    ]

    def __init__(self, on_change, on_path_manually_mounted, icon_size=16):
        self.icon_size = icon_size
        self.vm = Gio.VolumeMonitor.get()
        self.on_change_fn = on_change
        self.on_path_manually_mounted_fn = on_path_manually_mounted

        for sig in Places.VOLUME_MONITOR_SIGNALS:
            self.vm.connect(sig, self.on_change)

    def on_change(self, *args):
        self.on_change_fn()

    def get_places(self):
        places = []

        for drive in self.vm.get_connected_drives():
            self.add_drive(drive, places)

        for volume in self.vm.get_volumes():
            if not volume.get_drive():
                self.add_volume(volume, places)

        for mount in self.vm.get_mounts():
            if not mount.is_shadowed():
                self.add_mount(mount, places)

        places.sort(key=lambda p: p['label'].lower())

        places.insert(0, {
            'path': '/',
            'label': 'Computer',
            'icon': util.get_icon_path('drive-harddisk', self.icon_size)
        })

        return places

    def add_drive(self, drive, places):
        for volume in drive.get_volumes():
            self.add_volume(volume, places)

    def add_volume(self, volume, places):
        mount = volume.get_mount()
        if not mount:  # TODO Nautilus here also uses "or mount.is_shadowed()"?
            if volume.can_mount():
                volume_id = volume.get_identifier(Gio.VOLUME_IDENTIFIER_KIND_UNIX_DEVICE)
                places.append({
                    'path': 'command:mount:' + volume_id,
                    'label': volume.get_name(),
                    'needs_mounting': True,
                    'icon': self.get_icon(volume)
                })

    def add_mount(self, mount, places):
        item = {
            'path': mount.get_default_location().get_path(),
            'label': mount.get_name(),
            'icon': self.get_icon(mount),
        }
        # TODO:
        # if mount.can_unmount():
        #     item['with_command'] = {
        #         'command': 'command:unmount:' + ...
        #     }
        places.append(item)

    def get_icon(self, g_item):
        try:
            icon_name = g_item.get_icon().get_names()[0]
        except:
            icon_name = 'drive-harddisk'
        return util.get_icon_path(icon_name, self.icon_size, fallback='drive-harddisk')

    def mount_volume(self, volume_id):
        for volume in self.vm.get_volumes():
            if volume.get_identifier(Gio.VOLUME_IDENTIFIER_KIND_UNIX_DEVICE) == volume_id:
                volume.mount(
                    Gio.MountMountFlags.NONE,
                    None,
                    None,
                    self.on_user_mounted,
                    None,
                )

    def on_user_mounted(self, volume, *args):
        import time
        import os
        path = volume.get_mount().get_default_location().get_path()
        s = time.time()
        while time.time() - s < 2:
            try:
                os.listdir(path)
                break
            except:
                time.sleep(0.2)
        self.on_path_manually_mounted_fn(path)
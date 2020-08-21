#!/usr/bin/env python3
# This source file is part of Obozrenie
# Copyright 2015 Artem Vorotnikov

# For more information, see https://github.com/obozrenie/obozrenie

# Obozrenie is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.

# Obozrenie is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Obozrenie.  If not, see <http://www.gnu.org/licenses/>.

"""Useful functions for GTK+ UI"""

import ast
import os

from gi.repository import GLib, GdkPixbuf, Gtk


def get_icon_for_entry(entry, icon_type, icon_formats, icon_dir, width, height):
    icon_is_set = False
    for icon_format in icon_formats:
        try:
            icon = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(
                icon_dir, entry.lower() + "." + icon_format), width, height)
            icon_is_set = True
            break
        except GLib.GError:
            pass

    if icon_is_set is False:
        raise FileNotFoundError

    return icon


def get_icon_dict(key_list, icon_type, icon_formats, icon_dir, width, height, error_msg=None):
    """Loads icon pixbufs into memory for later usage"""
    icon_dict = {}
    for entry in key_list:
        try:
            icon_dict[entry] = get_icon_for_entry(
                entry, icon_type, icon_formats, icon_dir, width, height)
        except FileNotFoundError:
            if error_msg is not None:
                error_msg(entry)
            try:
                icon_dict[entry] = get_icon_for_entry(
                    "unknown", icon_type, icon_formats, icon_dir, width, height)
            except FileNotFoundError:
                icon_dict[entry] = None

    return icon_dict


def get_object_dict(builder, object_mapping):
    object_dict = {}

    builder_object = builder.get_object

    for entry in object_mapping:
        object_dict[object_mapping[entry]] = builder_object(entry)

    return object_dict


def set_object_properties(object_dict, property_dict):
    for entry in property_dict:
        widget = object_dict[entry]
        for property_entry in property_dict[entry]:
            widget.set_property(
                property_entry, property_dict[entry][property_entry])


def get_notebook_page_dict(notebook, widget_mapping):
    """Get mapping for notebook pages."""
    notebook_pages = {}
    for entry in widget_mapping:
        notebook_pages[entry] = notebook.page_num(widget_mapping[entry])

    return notebook_pages


def search_model(model, column, value):
    row_index = None
    for row in range(len(model)):
        if model[row][column] == value:
            row_index = row
            break
    return row_index


def set_widget_value(widget, value, treeview_colnum=0):
    """Applies setting to widget."""
    if value == 'None':
        value = None
    if isinstance(widget, Gtk.Adjustment):
        widget.set_property("value", int(value))
    elif isinstance(widget, Gtk.CheckButton) or isinstance(widget, Gtk.ToggleButton):
        try:
            value = ast.literal_eval(str(value))
        except ValueError:
            value = False
        widget.set_property("active", bool(value))
    elif isinstance(widget, Gtk.ComboBox) or isinstance(widget, Gtk.ComboBoxText):
        widget.set_property("active-id", str(value))
    elif isinstance(widget, Gtk.Entry):
        if value is None:
            value = ""
        widget.set_property("text", str(value))
        if value == "":
            widget.emit("changed")
    elif isinstance(widget, Gtk.Label):
        widget.set_property("label", str(value))
    elif isinstance(widget, Gtk.TreeView):
        model = widget.get_model()
        rownum = search_model(model, treeview_colnum, value)
        if rownum is not None:
            widget.get_selection().select_path(rownum)
    elif isinstance(widget, Gtk.TextBuffer):
        widget.set_property("text", value)


def get_widget_value(widget):
    """Fetches widget setting."""
    value = None
    if isinstance(widget, Gtk.Adjustment):
        value = widget.get_property("value")
    elif isinstance(widget, Gtk.CheckButton) or isinstance(widget, Gtk.ToggleButton):
        value = widget.get_property("active")
    elif isinstance(widget, Gtk.ComboBox) or isinstance(widget, Gtk.ComboBoxText):
        value = widget.get_property("active-id")
    elif isinstance(widget, Gtk.Entry):
        value = widget.get_property("text")
    elif isinstance(widget, Gtk.Label):
        value = widget.get_property("label")
    elif isinstance(widget, Gtk.TreeView):
        selection = None
        if isinstance(widget, Gtk.TreeSelection):
            selection = widget
        else:
            selection = widget.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            value = tuple(model[treeiter])
    elif isinstance(widget, Gtk.TextBuffer):
        value = widget.get_property("text")

    return value


def bind_widget_to_callback(widget, callback, *data):
    if isinstance(widget, Gtk.Entry) or isinstance(widget, Gtk.ComboBox) or isinstance(widget, Gtk.ComboBoxText):
        widget.connect("changed", callback, data)

    elif isinstance(widget, Gtk.CheckButton) or isinstance(widget, Gtk.ToggleButton):
        widget.connect("clicked", callback, data)

    elif isinstance(widget, Gtk.TreeView):
        widget.get_selection().connect("changed", callback, data)

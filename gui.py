import my
import wx
import wx.grid as grid
import wx.aui as aui
import wx.dataview as dv
import os
import sys
import json
import my_types
import logging
import threads
MY_SIZE = (348, 788)
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')


class DataTable(grid.GridTableBase):
    def __init__(self, data):
        logging.info('DataTable:__init__:')
        grid.GridTableBase.__init__(self)
        self.data = data
        self.colLabels = []
        self.colIds = []
        self.dataTypes = []
        # we need to store the row length and column length to see if the tables has changed size
        self._rows = self.GetNumberRows()

    def reset_view(self, my_grid):
        logging.info('DataTable:reset_view:')
        """
        (Grid) -> Reset the grid view.   Call this to
        update the grid if rows and columns have been added or deleted
        """
        my_grid.BeginBatch()

        current, new = self._rows, self.GetNumberRows()

        if new < current:
            msg = grid.GridTableMessage(self, grid.GRIDTABLE_NOTIFY_ROWS_DELETED, new, current - new)
            my_grid.ProcessTableMessage(msg)
        elif new > current:
            msg = grid.GridTableMessage(self, grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, new - current)
            my_grid.ProcessTableMessage(msg)

        my_grid.EndBatch()

        self._rows = self.GetNumberRows()

        # update the scrollbars and the displayed part of the grid
        my_grid.AdjustScrollbars()
        my_grid.ForceRefresh()

    def GetNumberRows(self):
        # logging.info('DataTable:GetNumberRows:')
        return len(self.data) + 1

    # --------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        # logging.info('DataTable:GetColLabelValue:')
        return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        # logging.info('DataTable:GetTypeName:')
        return self.dataTypes[col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, type_name):
        # logging.info('DataTable:CanGetValueAs:')
        col_type = self.dataTypes[col].split(':')[0]
        if type_name == col_type:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, type_name):
        # logging.info('DataTable:CanSetValueAs:')
        return self.CanGetValueAs(row, col, type_name)


class ActionsTable(DataTable):
    def __init__(self, data):
        logging.info('ActionsTable:__init__:')
        super().__init__(data)
        self.colLabels = ['Type', 'Generals', 'Delay', 'Active']
        self.colIds = ['type', 'generals', 'delay', 'active']
        self.dataTypes = [
                              grid.GRID_VALUE_CHOICE + ':load,unload,move,attack',
                              grid.GRID_VALUE_STRING,
                              grid.GRID_VALUE_NUMBER + ':0,99999999',
                              grid.GRID_VALUE_BOOL,
                         ]
    # --------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberCols(self):
        # logging.info('ActionsTable:GetNumberCols:')
        return 4

    def IsEmptyCell(self, row, col):
        # logging.info('ActionsTable:IsEmptyCell:')
        # pretending newer empty, so newer overflow
        return False

    def GetValue(self, row, col):
        # logging.info('ActionsTable:GetValue:')
        try:
            return self.data[row].get_data_for_table(self.colIds[col])
        except IndexError:
            empty = ['Click right to add', '', 0, False]
            return empty[col]

    def SetValue(self, row, col, value):
        # logging.info('ActionsTable:SetValue:')
        if col != 1:
            try:
                self.data[row].set_data_from_table(self.colIds[col], value)
            except IndexError:
                pass

    # --------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        # logging.info('ActionsTable:GetColLabelValue:')
        return super().GetColLabelValue(col)

    def GetTypeName(self, row, col):
        # logging.info('ActionsTable:GetTypeName:')
        return super().GetTypeName(row, col)

    def CanGetValueAs(self, row, col, type_name):
        # logging.info('ActionsTable:CanGetValueAs:')
        return super().CanGetValueAs(row, col, type_name)

    def CanSetValueAs(self, row, col, type_name):
        logging.info('ActionsTable:CanSetValueAs:')
        return super().CanSetValueAs(row, col, type_name)


class GeneralsTable(DataTable):
    def __init__(self, data):
        logging.info('GeneralsTable:__init__:')
        super().__init__(data)
        self.colLabels = ['Type', 'Name', 'Capacity']
        self.colIds = ['type', 'name', 'capacity']
        self.dataTypes = [
                              grid.GRID_VALUE_STRING,
                              grid.GRID_VALUE_STRING,
                              grid.GRID_VALUE_NUMBER + ':0,99999999'
                         ]
    # --------------------------------------------------
    # required methods for the wxPyGridTableBase interface

    def GetNumberCols(self):
        # logging.info('GeneralsTable:GetNumberCols:')
        return 3

    def IsEmptyCell(self, row, col):
        # logging.info('GeneralsTable:IsEmptyCell:')
        # pretending newer empty, so newer overflow
        return False

    def GetValue(self, row, col):
        # logging.info('GeneralsTable:GetValue:')
        try:
            return getattr(self.data[row], self.colIds[col])
        except IndexError:
            empty = ['Click right to add', '', 0]
            return empty[col]

    def SetValue(self, row, col, value):
        # logging.info('GeneralsTable:SetValue:')
        pass

    # --------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        # logging.info('GeneralsTable:GetColLabelValue:')
        return super().GetColLabelValue(col)

    def GetTypeName(self, row, col):
        # logging.info('GeneralsTable:GetTypeName:')
        return super().GetTypeName(row, col)

    def CanGetValueAs(self, row, col, type_name):
        # logging.info('GeneralsTable:CanGetValueAs:')
        return super().CanGetValueAs(row, col, type_name)

    def CanSetValueAs(self, row, col, type_name):
        # logging.info('GeneralsTable:CanSetValueAs:')
        return super().CanSetValueAs(row, col, type_name)


class DataGrid(grid.Grid):
    def __init__(self, parent, table, id_):
        logging.info('DataGrid:__init__:')
        grid.Grid.__init__(self, parent, id_)
        # TODO editing of some column only
        # self.EnableEditing(False)
        self.table = table
        self.left_clicked = None

        # The second parameter means that the grid is to take ownership of the
        # tables and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(self.table, True)
        self.SetSelectionMode(grid.Grid.GridSelectRows)
        self.SelectRow(0)
        self.SetCellSize(self.GetNumberRows()-1, 0, 1, self.GetNumberCols())
        self.SetRowLabelSize(grid.GRID_AUTOSIZE)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(True)

        self.Bind(grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_left_d_click)
        # self.GetGridWindow().Bind(wx.EVT_MOTION, self.on_mouse_over)
        self.Bind(grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)
        # self.Bind(grid.EVT_GRID_CELL_CHANGED, self.reset)
        # ---------------------------------------------------
        # ids for context menu
        self.context_menu_ids = dict()
        # self.make_context_menu_ids()

    def reset(self):
        logging.info('DataGrid:reset:')
        self.table.reset_view(self)
        for row in range(self.GetNumberRows()-1):
            self.SetCellSize(row, 0, 1, 1)
        self.SetCellSize(self.GetNumberRows()-1, 0, 1, self.GetNumberCols())

    # I do this because I don't like the default behaviour of not starting the
    # cell editor on double clicks, but only a second click.
    def on_left_d_click(self, evt):
        logging.info('DataGrid:on_left_d_click:')
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

    def make_context_menu_id(self, id_name, fun):
        if id_name not in self.context_menu_ids:
            self.context_menu_ids[id_name] = wx.NewIdRef()
            self.Bind(wx.EVT_MENU, fun, id=self.context_menu_ids[id_name])

    def make_context_menu_ids(self):
        logging.info('DataGrid:make_context_menu_ids:')

        self.make_context_menu_id('del_id', self.del_record)
        self.make_context_menu_id('move_up', self.move_up)
        self.make_context_menu_id('move_down', self.move_down)
        # self.make_context_menu_id('move_to', self.move_to)
        self.make_context_menu_id('activate', self.activate)
        self.make_context_menu_id('deactivate', self.deactivate)

    def on_right_click(self, event):
        logging.info('DataGrid:on_right_click:')
        row, col = event.GetRow(), event.GetCol()
        self.left_clicked = row

        # sending EVT_GRID_SELECT_CELL like event
        if col != 3:
            self.SelectRow(row)
            # noinspection PyPep8Naming
            MY_EVT_GRID_SELECT_CELL = wx.PyCommandEvent(grid.EVT_GRID_SELECT_CELL.typeId, self.GetId())
            MY_EVT_GRID_SELECT_CELL.row = row
            # posting event to handle it in AdventurePanel
            wx.PostEvent(self.GetEventHandler(), MY_EVT_GRID_SELECT_CELL)

        context_menu = wx.Menu()
        # adding menu in children classes
        self.on_right_click_add(context_menu, event)

        if col == 3:
            context_menu.AppendSeparator()
        else:
            if row < self.GetNumberRows() - 1:
                context_menu.AppendSeparator()
                context_menu.Append(self.context_menu_ids['del_id'], 'Delete')
                if row != 0:
                    context_menu.Append(self.context_menu_ids['move_up'], 'Move Up')
            if row < self.GetNumberRows() - 2:
                context_menu.Append(self.context_menu_ids['move_down'], 'Move Down')

        self.PopupMenu(context_menu)
        context_menu.Destroy()

    # def on_mouse_over(self, event):
    #     """
    #     Method to calculate where the mouse is pointing and
    #     then set the tooltip dynamically.
    #     """
    #
    #     # Use CalcUnscrolledPosition() to get the mouse position
    #     # within the
    #     # entire grid including what's offscreen
    #     x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
    #     row, col = self.XYToCell(x, y)
    #     # you only need these if you need the value in the cell
    #     if col == 1:
    #         gens = self.GetCellValue(row, col)
    #         if gens:
    #             event.GetEventObject().SetToolTip(gens.replace(', ', '\n'))
    #     event.Skip()

    def get_action(self, no):
        logging.info('DataGrid:get_action:')
        return self.table.data[no]

    def on_right_click_add(self, context_menu, event):
        logging.info('DataGrid:on_right_click_add:')
        # must be overridden in derived class to add context menu items
        pass

    def move_up(self, event):
        logging.info('DataGrid:move_up:')
        row = self.GetSelectedRows()[0]
        print('add-^')

    def move_down(self, event):
        logging.info('DataGrid:move_down:')
        row = self.GetSelectedRows()[0]
        print('add-v')

    def del_record(self, event):
        logging.info('DataGrid:del_record:')
        pass

    def activate(self, event):
        logging.info('DataGrid:activate:')
        pass

    def deactivate(self, event):
        logging.info('DataGrid:deactivate:')
        pass


class ActionsGrid(DataGrid):
    def __init__(self, parent, adventure):
        logging.info('ActionsGrid:__init__:')
        self.parent = parent
        self.actions = adventure.actions
        self.adventure = adventure
        self.table = ActionsTable(self.actions)
        self.id = wx.NewIdRef()
        super().__init__(parent, self.table, self.id)
        self.AutoSizeRows()

        self.GetGridWindow().Bind(wx.EVT_MOTION, self.on_mouse_over)

    # def on_right_click(self, event):
    #     if event.GetCol() == 1:
    #         self.action_context_menu(event)

    def on_mouse_over(self, event):
        # logging.info('ActionsGrid:on_mouse_over:')
        """
        Method to calculate where the mouse is pointing and
        then set the tooltip dynamically.
        """

        # Use CalcUnscrolledPosition() to get the mouse position
        # within the
        # entire grid including what's offscreen
        x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        row, col = self.XYToCell(x, y)
        # you only need these if you need the value in the cell
        if col == 1:
            gens = self.GetCellValue(row, col)
            if gens:
                event.GetEventObject().SetToolTip(gens)
        event.Skip()

    def make_context_menu_ids(self):
        logging.info('ActionsGrid:make_context_menu_ids:')
        for act in my_types.action_types:
            if 'id_ref' not in act:
                act['id_ref'] = wx.NewIdRef()
                self.Bind(wx.EVT_MENU, self.add_record, id=act['id_ref'])
        for gen in self.adventure.generals:
            if not gen.id_ref:
                gen.id_ref = wx.NewIdRef()
                self.Bind(wx.EVT_MENU, self.add_general_to_record, id=gen.id_ref)
        super().make_context_menu_ids()

    def add_general_to_record(self, event):
        logging.info('ActionsGrid:add_general_to_record:')
        evt_id = event.GetId()
        row = self.GetSelectedRows()[0]
        for gen in self.adventure.generals:
            if gen.id_ref == evt_id:
                self.actions[row].add_general(gen)
                print('adding', gen.name, 'to', self.actions[row].type)
                self.parent.parent.generals_edt.show_generals(self.actions[row].generals)
                break
        self.reset()
        self.AutoSizeRow(row)

    def add_record(self, event):
        logging.info('ActionsGrid:add_record:')
        evt_id = event.GetId()
        row = self.GetSelectedRows()[0]
        for act in my_types.action_types:
            if act['id_ref'] == evt_id:
                self.adventure.add_action(row, **act)
                break
        self.reset()

    def del_record(self, event):
        logging.info('ActionsGrid:del_record:')
        try:
            self.adventure.remove_action(self.GetSelectedRows()[0])
        except IndexError:
            return
        self.reset()

    def move_up(self, event):
        logging.info('ActionsGrid:move_up:')
        row = self.GetSelectedRows()[0]
        self.adventure.move_action(row, row-1)
        self.reset()
        self.SelectRow(row-1)

    def move_down(self, event):
        logging.info('ActionsGrid:move_down:')
        row = self.GetSelectedRows()[0]
        self.adventure.move_action(row, row+1)
        self.reset()
        self.SelectRow(row+1)

    def on_right_click_add(self, context_menu, event):
        logging.info('ActionsGrid:on_right_click_add:')
        self.make_context_menu_ids()
        row, col = event.GetRow(), event.GetCol()
        if col == 0:
            for act in my_types.action_types:
                context_menu.Append(act['id_ref'], act['type'])
        elif col == 1:
            for gen in self.adventure.generals:
                context_menu.Append(gen.id_ref, gen.name or gen.type)
        elif col == 3:
            context_menu.Append(self.context_menu_ids['activate'], 'Activate selected')
            context_menu.Append(self.context_menu_ids['deactivate'], 'Deactivate selected')

    def activate(self, event):
        logging.info('ActionsGrid:on_right_click_add:')
        self.adventure.set_actions_active(self.GetSelectedRows(), True)
        self.reset()

    def deactivate(self, event):
        logging.info('ActionsGrid:on_right_click_add:')
        self.adventure.set_actions_active(self.GetSelectedRows(), False)
        self.reset()


class GeneralsGrid(DataGrid):
    def __init__(self, parent, adventure):
        logging.info('GeneralsGrid:__init__:')
        self.parent = parent
        self.adventure = adventure
        self.generals = adventure.generals
        self.my_generals = parent.parent.my_generals
        self.table = GeneralsTable(self.generals)
        self.id = wx.NewIdRef()
        super().__init__(parent, self.table, self.id)

    def make_context_menu_ids(self):
        logging.info('GeneralsGrid:make_context_menu_ids:')
        for gen in self.my_generals:
            if 'id_ref' not in gen:
                gen['id_ref'] = wx.NewIdRef()
                self.Bind(wx.EVT_MENU, self.add_record, id=gen['id_ref'])
        super().make_context_menu_ids()

    def add_record(self, event):
        logging.info('GeneralsGrid:add_record:')
        evt_id = event.GetId()
        row = self.GetSelectedRows()[0]
        for gen in self.my_generals:
            if gen['id_ref'] == evt_id:
                self.adventure.add_general(row, **gen)
                self.parent.parent.generals_edt.show_generals([self.adventure.generals[row], ])
                break
        self.reset()
        self.SelectRow(row)

    def del_record(self, event):
        logging.info('GeneralsGrid:del_record:')
        try:
            row = self.GetSelectedRows()[0]
            self.adventure.remove_general(row)
        except IndexError:
            return
        self.reset()
        self.SelectRow(row)

    def move_up(self, event):
        logging.info('GeneralsGrid:move_up:')
        row = self.GetSelectedRows()[0]
        self.adventure.move_general(row, row-1)
        self.reset()
        self.SelectRow(row-1)

    def move_down(self, event):
        logging.info('GeneralsGrid:move_down:')
        row = self.GetSelectedRows()[0]
        self.adventure.move_general(row, row+1)
        self.reset()
        self.SelectRow(row+1)

    def on_right_click_add(self, context_menu, event):
        logging.info('GeneralsGrid:on_right_click_add:')
        self.make_context_menu_ids()
        generals_names = self.adventure.get_generals_names()
        for gen in self.my_generals:
            if gen['name'] not in generals_names:
                context_menu.Append(gen['id_ref'], gen['name'])

    # def on_right_click(self, event):
    #     if event.GetCol() == 1:
    #         self.action_context_menu(event)

    # def on_mouse_over(self, event):
    #     """
    #     Method to calculate where the mouse is pointing and
    #     then set the tooltip dynamically.
    #     """
    #
    #     # Use CalcUnscrolledPosition() to get the mouse position
    #     # within the
    #     # entire grid including what's offscreen
    #     x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
    #     row, col = self.XYToCell(x, y)
    #     # you only need these if you need the value in the cell
    #     if col == 1:
    #         gens = self.GetCellValue(row, col)
    #         if gens:
    #             event.GetEventObject().SetToolTip(gens.replace(', ', '\n'))
    #     event.Skip()


class MainGrid(DataGrid):
    def __init__(self, parent, tasks):
        logging.info('GeneralsGrid:__init__:')
        self.parent = parent
        self.tasks = tasks
        self.table = GeneralsTable(self.tasks)
        self.id = wx.NewIdRef()
        super().__init__(parent, self.tasks, self.id)


class GeneralEdit(wx.Panel):
    def __init__(self, parent, general=None):
        logging.info('GeneralEdit:__init__:')
        if not general:
            general = my_types.General(parent)
        self.general = general
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN | wx.FULL_REPAINT_ON_RESIZE)
        gbs = self.gbs = wx.GridBagSizer(vgap=0, hgap=0)

        def label(text):
            txt = wx.StaticText(self, -1, text)
            # noinspection PyUnresolvedReferences
            txt.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            return txt

        units_ = my_types.elite if general.elite else my_types.not_elite
        for i, key in enumerate(units_):
            gbs.Add(label(key + ':'), (int(i / 3) * 2, i % 3 + 1))

        gbs.Add(label("Delay"), (7, 1))

        self.army = army = {}
        keys = general.elite_keys if general.elite else general.keys
        for count, key in enumerate(keys):
            spin_ctrl = wx.SpinCtrl(self, id=wx.ID_ANY, style=wx.SP_ARROW_KEYS, min=0, name=key)
            gbs.Add(spin_ctrl, (int(count / 3) * 2 + 1, count % 3 + 1))
            self.army.setdefault(key, spin_ctrl)

        self.delay = wx.SpinCtrl(self, id=wx.ID_ANY, style=wx.SP_ARROW_KEYS, min=0)
        gbs.Add(self.delay, (8, 1))
        separator = wx.StaticLine(self, id=wx.ID_ANY, size=wx.Size(300, 1), style=wx.LI_HORIZONTAL)
        gbs.Add(separator, (6, 1), (1, 3), flag=wx.ALIGN_CENTER)

        # ----------------------------------------------------
        def check_box(text):
            c_box = wx.CheckBox(self, id=wx.ID_ANY, label=text)
            # noinspection PyUnresolvedReferences
            c_box.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            return c_box
        check_box_sizer = wx.BoxSizer(wx.VERTICAL)
        self.preset = check_box('Preset')
        self.init = check_box('Init')
        check_box_sizer.Add(self.preset, 0, wx.EXPAND | wx.ALL, 0)
        check_box_sizer.Add(self.init, 0, wx.EXPAND | wx.ALL, 0)
        gbs.Add(check_box_sizer, (7, 2), (2, 1), flag=wx.ALIGN_CENTER)

        # -----------------------------------------------------
        check_box2_sizer = wx.BoxSizer(wx.VERTICAL)
        self.retreat = check_box('Retreat')
        self.elite = check_box('Elite Army')
        check_box2_sizer.Add(self.retreat, 0, wx.EXPAND | wx.ALL, 0)
        check_box2_sizer.Add(self.elite, 0, wx.EXPAND | wx.ALL, 0)
        gbs.Add(check_box2_sizer, (7, 3), (2, 1), flag=wx.ALIGN_CENTER)
        # -----------------------------------------------------
        # For layout
        gbs.AddGrowableCol(0)
        gbs.Add(1, 1, (0, 0))
        gbs.Add(1, 1, (0, 4))
        gbs.AddGrowableCol(4)
        # -----------------------------------------------------
        self.gbs = gbs
        self.SetSizerAndFit(gbs)
        # -----------------------------------------------------
        # setting values
        for key, units in army.items():
            units.SetMax(general.capacity)
            units.SetValue(general.army.get(key, 0))
        self.delay.SetValue(general.delay)
        self.preset.SetValue(general.preset)
        self.init.SetValue(general.init)
        self.retreat.SetValue(general.retreat)
        self.elite.SetValue(general.elite)
        # -----------------------------------------------------
        # binding events to set values
        self.Bind(wx.EVT_SPINCTRL, self.on_army_change)
        self.delay.Bind(wx.EVT_SPINCTRL, self.on_delay_change)
        self.preset.Bind(wx.EVT_CHECKBOX, self.on_preset_change)
        self.init.Bind(wx.EVT_CHECKBOX, self.on_init_change)
        self.retreat.Bind(wx.EVT_CHECKBOX, self.on_retreat_change)
        self.elite.Bind(wx.EVT_CHECKBOX, self.on_elite_change)

    @classmethod
    def get_min_size(cls, parent):
        logging.info('GeneralEdit:get_min_size:')
        return cls(parent).GetMinSize()

    @classmethod
    def get_size(cls, parent):
        logging.info('GeneralEdit:get_size:')
        return cls(parent).GetSize()

    def on_army_change(self, event):
        logging.info('GeneralEdit:on_army_change:')
        self.general.set_units(event.GetEventObject().GetName(), event.GetPosition())

    def on_delay_change(self, event):
        logging.info('GeneralEdit:on_delay_change:')
        self.general.delay = event.GetPosition()

    def on_preset_change(self, event):
        logging.info('GeneralEdit:on_preset_change:')
        self.general.preset = event.IsChecked()

    def on_init_change(self, event):
        logging.info('GeneralEdit:on_init_change:')
        self.general.init = event.IsChecked()

    def on_retreat_change(self, event):
        logging.info('GeneralEdit:on_retreat_change:')
        self.general.retreat = event.IsChecked()

    def on_elite_change(self, event):
        logging.info('GeneralEdit:on_elite_change:')
        self.general.elite = event.IsChecked()
        keys_to_remove = self.general.keys if self.general.elite else self.general.elite_keys
        for key in keys_to_remove:
            self.general.army.pop(key, 0)


class HelpPage(wx.Panel):
    def __init__(self, parent):
        logging.info('HelpPage:__init__:')
        wx.Panel.__init__(self, parent, -1,
                          style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN | wx.FULL_REPAINT_ON_RESIZE)
        sizer = self.sizer = wx.BoxSizer()
        self.SetMinSize(GeneralEdit.get_size(self))
        self.DestroyChildren()

        def label(text):
            txt = wx.StaticText(self, -1, text)
            # noinspection PyUnresolvedReferences
            txt.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            return txt
        # help_txt = "Move page tabs sideways, to change generals order.\n" \
        #            "Close tab, to delete general from action.\n" \
        #            "Can not remove generals from adventure this way"
        help_txt = "Deleting, moving generals in action not implemented yet.\n"
        sizer.Add(label(help_txt), 0, wx.EXPAND)
        self.SetSizer(sizer)


class GeneralsEdit(aui.AuiNotebook):
    """
    Book with GeneralEdit pages, and HelpPage page
    """

    def __init__(self, parent):
        logging.info('GeneralsEdit:__init__:')
        self._notebook_style = aui.AUI_NB_WINDOWLIST_BUTTON | aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_CLOSE_ON_ALL_TABS
        self.parent = parent
        self.pages = list()
        aui.AuiNotebook.__init__(self, parent, -1, wx.Point(0, 0), style=self._notebook_style)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_close_page)
        self.help_page = HelpPage(self)
        self.AddPage(self.help_page, 'Help')

    def show_generals(self, generals):
        logging.info('GeneralsEdit:show_generals:')
        generals_add_index = self.GetPageIndex(self.help_page)
        # delete all pages, accept help_page page
        for p in range(generals_add_index-1, -1, -1):
            self.DeletePage(p)
        self.pages = list()
        # add pages from new action before help_page page
        for g_no, general in enumerate(generals):
            self.pages.append(GeneralEdit(self, general))
            self.InsertPage(g_no, self.pages[-1], '{} ({})'.format(general.name or general.type, general.id))
        # set help_page page size, to math others pages
        if self.pages:
            self.help_page.SetMinSize(self.pages[0].GetMinSize())
        # select last general
        if 'g_no' in locals():
            # noinspection PyUnboundLocalVariable
            self.SetSelection(g_no)

    def on_close_page(self, event):
        logging.info('GeneralsEdit:on_close_page:')
        # prevent help_page page from close
        if event.GetSelection() == self.GetPageIndex(self.help_page):
            event.Veto()


class Splitter(wx.SplitterWindow):
    """GeneralsGrid and ActionsGrid with splitter"""
    def __init__(self, parent, adventure):
        logging.info('Splitter:__init__:')
        self.parent = parent
        wx.SplitterWindow.__init__(self, parent, wx.ID_ANY, style=wx.SP_LIVE_UPDATE)
        self.actions_grid = ActionsGrid(self, adventure)
        self.generals_grid = GeneralsGrid(self, adventure)
        self.SetMinimumPaneSize(20)
        self.SplitHorizontally(self.generals_grid, self.actions_grid, 100)


class AdventurePanel(wx.Panel):
    def __init__(self, parent, adventure):
        logging.info('AdventurePanel:__init__:')
        wx.Panel.__init__(self, parent, wx.ID_ANY,
                          style=wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE)

        self.last_row = 9999999
        self.last_grid_id = None
        self.my_generals = my.load_generals()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.tables = Splitter(self, adventure)
        self.sizer.Add(self.tables, 1, wx.EXPAND)
        self.generals_edt = GeneralsEdit(self)
        self.sizer.Add(self.generals_edt, 0, wx.EXPAND)
        self.Bind(grid.EVT_GRID_SELECT_CELL, self.on_select_cell)
        self.Bind(grid.EVT_GRID_RANGE_SELECT, self.on_select_cell)
        self.generals_edt.Show()
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.Fit()

    def on_select_cell(self, event):
        logging.info('AdventurePanel:on_select_cell:')
        if isinstance(event, grid.GridEvent):
            row = event.GetRow()
        elif isinstance(event, grid.GridRangeSelectEvent):
            row = 8888888
        else:
            row = event.row
        if event.GetId() == self.last_grid_id:
            if event.GetId() == self.tables.actions_grid.id:
                self.tables.generals_grid.ClearSelection()
            elif event.GetId() == self.tables.generals_grid.id:
                self.tables.actions_grid.ClearSelection()
        if self.last_grid_id != event.GetId() or self.last_row != row:
            generals = []
            if event.GetId() == self.tables.actions_grid.id:
                if len(self.tables.actions_grid.GetSelectedRows()) == 1:
                    try:
                        generals = self.tables.actions_grid.get_action(row).get_generals()
                    except IndexError:
                        pass
            elif event.GetId() == self.tables.generals_grid.id:
                if len(self.tables.generals_grid.GetSelectedRows()) == 1:
                    try:
                        generals = [self.tables.generals_grid.generals[row]]
                    except IndexError:
                        pass
            self.generals_edt.show_generals(generals)
            self.last_row = row
            self.last_grid_id = event.GetId()


class Frame(wx.Frame):
    def __init__(self, parent):
        logging.info('Frame:__init__:')
        wx.Frame.__init__(self, parent, -1, "Custom Table, data driven Grid  Demo",
                          style=wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE)
        self.parent = parent
        self.menu_bar_ids = {}
        self._notebook_style = aui.AUI_NB_WINDOWLIST_BUTTON | aui.AUI_NB_SCROLL_BUTTONS
        self.main_notebook = aui.AuiNotebook(self, wx.ID_ANY, style=self._notebook_style)
        # empty adventure
        self.status_bar = self.CreateStatusBar(1)
        self.adventure = my_types.Adventure(name='Empty')
        self.tasks = None
        # self.adventure.actions = [my_types.Action(self)]
        self.adventure_panel = None
        # self.main_page = MainGrid(self, self.tasks)
        # self.main_notebook.AddPage(self.main_page, 'Tasks')
        self.open_adventure_tab()
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(grid.EVT_GRID_COL_SIZE, self.on_size)

        self.make_menu_bar()
        self.main_notebook.Fit()
        self.SetMinSize(size=MY_SIZE)
        self.Fit()

    def open_adventure_tab(self):
        logging.info('Frame:open_adventure_tab:')
        self.main_notebook.DeletePage(0)
        self.adventure_panel = AdventurePanel(self, self.adventure)
        self.main_notebook.AddPage(self.adventure_panel, self.adventure.name)

    def open_adv(self, event):
        logging.info('Frame:open_adv:')
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd() + '/save',
            defaultFile="",
            wildcard="Adventure file (*.adv)|*.adv",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.adventure = my_types.Adventure.open(path)
            self.open_adventure_tab()
        dlg.Destroy()

    # TODO temp
    def open_from_json(self, event):
        logging.info('Frame:open_from_json:')
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd() + '/data',
            defaultFile="",
            wildcard="Adventure file (*.json)|*.json",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            with open(path) as f:
                j_data = json.load(f)
            generals = [my_types.General(**gen) for gen in j_data['generals']]
            actions = [my_types.Action(self, **action) for action in j_data['actions']]
            adv_from_json = my_types.Adventure(name=path.split('\\' if sys.platform == 'win32' else '/')[-2])
            adv_from_json.generals = generals
            adv_from_json.actions = actions
            self.adventure = adv_from_json
            self.open_adventure_tab()
        dlg.Destroy()

    # TODO temp
    def save_as_json(self, event):
        logging.info('Frame:save_as_json:')
        dlg = wx.FileDialog(
            self, message="Save file as ...",
            defaultDir=os.getcwd() + '/data',
            defaultFile="",
            wildcard="Adventure file (*.json)|*.json",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            path += '.json' if path[-5:] != '.json' else ''
            with open(path, 'w') as f:
                json.dump(self.adventure.as_json(), f, indent=2)
        dlg.Destroy()

    def save_adv(self, event):
        logging.info('Frame:save_adv:')
        dlg = wx.FileDialog(
            self, message="Save file as ...",
            defaultDir=os.getcwd() + '/save',
            defaultFile="",
            wildcard="Adventure file (*.adv)|*.adv",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.adventure.save(path)
        dlg.Destroy()

    def make_menu_bar(self):
        logging.info('Frame:make_menu_bar:')
        menu_bar = wx.MenuBar()
        menu_f = wx.Menu()
        self.menu_bar_ids['save'] = wx.NewIdRef()
        menu_f.Append(self.menu_bar_ids['save'], '&Save')
        self.Bind(wx.EVT_MENU, self.save_adv, id=self.menu_bar_ids['save'])
        self.menu_bar_ids['open'] = wx.NewIdRef()
        menu_f.Append(self.menu_bar_ids['open'], '&Open')
        self.Bind(wx.EVT_MENU, self.open_adv, id=self.menu_bar_ids['open'])
        menu_bar.Append(menu_f, '&File')
        # TODO 6 lines temp
        self.menu_bar_ids['fromJson'] = wx.NewIdRef()
        menu_f.Append(self.menu_bar_ids['fromJson'], '&fromJson')
        self.Bind(wx.EVT_MENU, self.open_from_json, id=self.menu_bar_ids['fromJson'])
        self.menu_bar_ids['toJson'] = wx.NewIdRef()
        menu_f.Append(self.menu_bar_ids['toJson'], '&toJson')
        self.Bind(wx.EVT_MENU, self.save_as_json, id=self.menu_bar_ids['toJson'])
        # TODO start adv action
        menu_adv = wx.Menu()
        self.menu_bar_ids['start'] = wx.NewIdRef()
        menu_adv.Append(self.menu_bar_ids['start'], 'Play')
        self.Bind(wx.EVT_MENU, self.on_start, id=self.menu_bar_ids['start'])
        menu_bar.Append(menu_adv, 'Start')

        self.SetMenuBar(menu_bar)

    def on_start(self, event):
        worker = threads.StartAdventure(self, 60, self.adventure)
        worker.start()

    def on_size(self, event):
        logging.info('Frame:on_size:')
        width, height = self.GetClientSize()
        action_panel = self.adventure_panel.tables.actions_grid
        action_panel.SetSize(width, height)
        action_panel.SetColSize(1, width
                                - sum(action_panel.GetColSize(col) for col in (0, 2, 3))
                                - action_panel.GetRowLabelSize())
        self.main_notebook.SetSize(self.GetClientSize())


if __name__ == '__main__':
    app = wx.App()
    frame = Frame(None)
    frame.Show(True)
    app.MainLoop()

import my
import wx
import wx.grid as grid
import wx.aui as aui
import wx.dataview as dv
import sys
import json
import my_types
MY_SIZE = (348, 788)


class DataTable(grid.GridTableBase):
    def __init__(self, data, log):
        grid.GridTableBase.__init__(self)
        self.log = log
        self.data = data
        self.colLabels = []
        self.colIds = []
        self.dataTypes = []

    def GetNumberRows(self):
        return len(self.data)

    # --------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return self.colLabels[col]

    # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
    def GetTypeName(self, row, col):
        return self.dataTypes[col]

    # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
    def CanGetValueAs(self, row, col, type_name):
        col_type = self.dataTypes[col].split(':')[0]
        if type_name == col_type:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, type_name):
        return self.CanGetValueAs(row, col, type_name)


class ActionsTable(DataTable):
    def __init__(self, data, log):
        super().__init__(data, log)
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
        return 4

    def IsEmptyCell(self, row, col):
        # pretending newer empty, so newer overflow
        return False

    def GetValue(self, row, col):
        try:
            return self.data[row].get_data_for_table(self.colIds[col])
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        if col != 1:
            self.data[row].set_data_from_table(self.colIds[col], value)

    # --------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return super().GetColLabelValue(col)

    def GetTypeName(self, row, col):
        return super().GetTypeName(row, col)

    def CanGetValueAs(self, row, col, type_name):
        return super().CanGetValueAs(row, col, type_name)

    def CanSetValueAs(self, row, col, type_name):
        return super().CanSetValueAs(row, col, type_name)


class GeneralsTable(DataTable):
    def __init__(self, data, log):
        super().__init__(data, log)
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
        return 3

    def IsEmptyCell(self, row, col):
        # pretending newer empty, so newer overflow
        return False

    def GetValue(self, row, col):
        try:
            return self.data[row][self.colIds[col]]
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        pass

    # --------------------------------------------------
    # Some optional methods

    # Called when the grid needs to display labels
    def GetColLabelValue(self, col):
        return super().GetColLabelValue(col)

    def GetTypeName(self, row, col):
        return super().GetTypeName(row, col)

    def CanGetValueAs(self, row, col, type_name):
        return super().CanGetValueAs(row, col, type_name)

    def CanSetValueAs(self, row, col, type_name):
        return super().CanSetValueAs(row, col, type_name)


class DataGrid(grid.Grid):
    def __init__(self, parent, table, log):
        grid.Grid.__init__(self, parent, -1)
        self.table = table

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(self.table, True)
        self.SetSelectionMode(grid.Grid.GridSelectRows)
        self.SelectRow(0)
        self.SetRowLabelSize(grid.GRID_AUTOSIZE)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(True)

        self.Bind(grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_left_d_click)
        # self.GetGridWindow().Bind(wx.EVT_MOTION, self.on_mouse_over)
        self.Bind(grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_right_click)
        # ---------------------------------------------------
        # ids for context menu
        self.add_below_id = wx.NewIdRef()
        self.add_above_id = wx.NewIdRef()
        self.Bind(wx.EVT_MENU, self.add_below, id=self.add_below_id)
        self.Bind(wx.EVT_MENU, self.add_above, id=self.add_above_id)

    # I do this because I don't like the default behaviour of not starting the
    # cell editor on double clicks, but only a second click.
    def on_left_d_click(self, evt):
        if self.CanEnableCellControl():
            self.EnableCellEditControl()

    def on_right_click(self, event):
        if event.GetCol() == 1:
            self.action_context_menu(event)

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
        return self.table.data[no]

    def action_context_menu(self, event):

        self.SelectRow(event.GetRow())
        # noinspection PyPep8Naming
        MY_EVT_GRID_SELECT_CELL = wx.PyCommandEvent(grid.EVT_GRID_SELECT_CELL.typeId, self.GetId())
        MY_EVT_GRID_SELECT_CELL.row = event.GetRow()
        wx.PostEvent(self.GetEventHandler(), MY_EVT_GRID_SELECT_CELL)
        context_menu = wx.Menu()
        context_menu.Append(self.add_above_id, 'Add action above')
        context_menu.Append(self.add_below_id, 'Add action below')
        self.PopupMenu(context_menu)
        context_menu.Destroy()

    def add_above(self, event):
        row = self.GetSelectedRows()[0]
        print('add-^')

    def add_below(self, event):
        row = self.GetSelectedRows()[0]
        print('add-v')
        print(GeneralEdit.get_min_size(self))


class ActionsGrid(DataGrid):
    def __init__(self, parent, name, log):
        with open(my.get_last_filename(name)) as f:
            data = json.load(f)
            self.actions = [my_types.Action(self, **action) for action in data['actions']]
        self.table = ActionsTable(self.actions, log)
        super().__init__(parent, self.table, log)

        self.GetGridWindow().Bind(wx.EVT_MOTION, self.on_mouse_over)

    # def on_right_click(self, event):
    #     if event.GetCol() == 1:
    #         self.action_context_menu(event)

    def on_mouse_over(self, event):
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
                event.GetEventObject().SetToolTip(gens.replace(', ', '\n'))
        event.Skip()

    # def get_action(self, no):
    #     return self.table.data[no]

    # def action_context_menu(self, event):
    #
    #     self.SelectRow(event.GetRow())
    #     # noinspection PyPep8Naming
    #     MY_EVT_GRID_SELECT_CELL = wx.PyCommandEvent(grid.EVT_GRID_SELECT_CELL.typeId, self.GetId())
    #     MY_EVT_GRID_SELECT_CELL.row = event.GetRow()
    #     wx.PostEvent(self.GetEventHandler(), MY_EVT_GRID_SELECT_CELL)
    #     context_menu = wx.Menu()
    #     context_menu.Append(self.add_above_id, 'Add action above')
    #     context_menu.Append(self.add_below_id, 'Add action below')
    #     self.PopupMenu(context_menu)
    #     context_menu.Destroy()
    #
    # def add_above(self, event):
    #     row = self.GetSelectedRows()[0]
    #     print('add-^')
    #
    # def add_below(self, event):
    #     row = self.GetSelectedRows()[0]
    #     print('add-v')
    #     print(GeneralEdit.get_min_size(self))


class GeneralsGrid(DataGrid):
    def __init__(self, parent, log):
        self.data = my.load_generals()
        self.table = GeneralsTable(self.data, log)
        super().__init__(parent, self.table, log)

        # self.GetGridWindow().Bind(wx.EVT_MOTION, self.on_mouse_over)

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


class GeneralEdit(wx.Panel):
    def __init__(self, parent, general=None):
        if not general:
            general = my_types.General(parent)
        self.general = general
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN | wx.FULL_REPAINT_ON_RESIZE)
        gbs = self.gbs = wx.GridBagSizer(vgap=0, hgap=0)

        def label(text):
            txt = wx.StaticText(self, -1, text)
            # noinspection PyUnresolvedReferences
            txt.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL))
            return txt
        gbs.Add(label("Recruit:"), (0, 1))
        gbs.Add(label("Bowmen:"), (0, 2))
        gbs.Add(label("Militia:"), (0, 3))
        gbs.Add(label("Cavalry:"), (2, 1))
        gbs.Add(label("Longbowman:"), (2, 2))
        gbs.Add(label("Soldier:"), (2, 3))
        gbs.Add(label("Crossbowman:"), (4, 1))
        gbs.Add(label("Elite soldier:"), (4, 2))
        gbs.Add(label("Cannoneer:"), (4, 3))
        gbs.Add(label("Delay"), (7, 1))

        self.army = army = {}
        for count, key in enumerate(general.army.keys()):
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
            c_box.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL))
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
        self.learned = check_box('Coord setted')
        self.learned.Disable()
        check_box2_sizer.Add(self.retreat, 0, wx.EXPAND | wx.ALL, 0)
        check_box2_sizer.Add(self.learned, 0, wx.EXPAND | wx.ALL, 0)
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
            units.SetValue(general.army[key])
        self.delay.SetValue(general.delay)
        self.preset.SetValue(general.preset)
        self.init.SetValue(general.init)
        self.retreat.SetValue(general.retreat)
        self.learned.SetValue(general.relative_coordinates is not None)
        # -----------------------------------------------------
        # binding events to set values
        self.Bind(wx.EVT_SPINCTRL, self.on_army_change)
        self.delay.Bind(wx.EVT_SPINCTRL, self.on_delay_change)
        self.preset.Bind(wx.EVT_CHECKBOX, self.on_preset_change)
        self.init.Bind(wx.EVT_CHECKBOX, self.on_init_change)
        self.retreat.Bind(wx.EVT_CHECKBOX, self.on_retreat_change)

    @classmethod
    def get_min_size(cls, parent):
        return cls(parent).GetMinSize()

    @classmethod
    def get_size(cls, parent):
        return cls(parent).GetSize()

    def on_army_change(self, event):
        self.general.set_units(event.GetEventObject().GetName(), event.GetPosition())

    def on_delay_change(self, event):
        self.general.delay = event.GetPosition()

    def on_preset_change(self, event):
        self.general.preset = event.IsChecked()

    def on_init_change(self, event):
        self.general.init = event.IsChecked()

    def on_retreat_change(self, event):
        self.general.retreat = event.IsChecked()


class GeneralAdd(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1,
                          style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN | wx.FULL_REPAINT_ON_RESIZE)
        sizer = self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetMinSize(GeneralEdit.get_size(self))
        self.DestroyChildren()

        def label(text):
            txt = wx.StaticText(self, -1, text)
            # noinspection PyUnresolvedReferences
            txt.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL))
            return txt
        sizer.Add(label("Double click on general to add"), 0, wx.EXPAND)

        self.dvlc = dvlc = dv.DataViewListCtrl(self)

        # Give it some columns.
        # The ID col we'll customize a bit:
        dvlc.AppendTextColumn('type')
        dvlc.AppendTextColumn('name')
        dvlc.AppendTextColumn('capacity')

        # Load the data. Each item (row) is added as a sequence of values
        # whose order matches the columns
        for gen in my.load_generals():
            dvlc.AppendItem((gen['type'], gen['name'], str(gen['capacity'])))
        sizer.Add(dvlc, 1, wx.EXPAND)
        self.SetSizer(sizer)


class GeneralsEdit(aui.AuiNotebook):
    """
    A simple window that is used as sizer items in the tests below to
    show how the various sizers work.
    """

    def __init__(self, parent):
        self._notebook_style = aui.AUI_NB_WINDOWLIST_BUTTON | aui.AUI_NB_SCROLL_BUTTONS | aui.AUI_NB_CLOSE_ON_ALL_TABS
        self.parent = parent
        self.pages = list()
        aui.AuiNotebook.__init__(self, parent, -1, wx.Point(0, 0), style=self._notebook_style)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_close_page)
        self.generals_add = GeneralAdd(self)
        self.AddPage(self.generals_add, 'Add general')
        self.show_generals(0)

    def show_generals(self, action_no):
        generals = self.parent.table.get_action(action_no).get_generals()
        generals_add_index = self.GetPageIndex(self.generals_add)
        # delete all pages, accept generals_add page
        for p in range(generals_add_index-1, -1, -1):
            self.DeletePage(p)
        self.pages = list()
        # add pages from new action before generals_add page
        for g_no, general in enumerate(generals):
            self.pages.append(GeneralEdit(self, general))
            self.InsertPage(g_no, self.pages[-1], '{} ({})'.format(general.type, general.id))
        # set generals_add page size, to math others pages
        if self.pages:
            self.generals_add.SetMinSize(self.pages[0].GetMinSize())
        # select last general
        if 'g_no' in locals():
            # noinspection PyUnboundLocalVariable
            self.SetSelection(g_no)

    def on_close_page(self, event):
        # prevent generals_add page from close
        if event.GetSelection() == self.GetPageIndex(self.generals_add):
            event.Veto()


class AdventurePanel(wx.Panel):
    def __init__(self, parent, log):
        wx.Panel.__init__(self, parent, wx.ID_ANY,
                          style=wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE)

        self.last_row = 9999999
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.table = ActionsGrid(self, 'CR', log)
        self.sizer.Add(self.table, 1, wx.EXPAND)
        self.generals_edt = GeneralsEdit(self)
        self.sizer.Add(self.generals_edt, 0, wx.EXPAND)
        self.Bind(grid.EVT_GRID_SELECT_CELL, self.on_select_cell)

        self.generals_edt.Show()
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.Fit()

    def on_select_cell(self, event):
        if isinstance(event, grid.GridEvent):
            row = event.GetRow()
        else:
            row = event.row
        if self.last_row != row:
            self.generals_edt.show_generals(row)
            self.last_row = row


class Frame(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, "Custom Table, data driven Grid  Demo",
                          style=wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE)

        self._notebook_style = aui.AUI_NB_WINDOWLIST_BUTTON | aui.AUI_NB_SCROLL_BUTTONS
        self.main_notebook = aui.AuiNotebook(self, wx.ID_ANY, style=self._notebook_style)
        self.action_adv_panel = AdventurePanel(self, log)
        self.main_notebook.AddPage(self.action_adv_panel, 'Adventure Actions')
        self.generals_adv_panel = GeneralsGrid(self, log)
        self.main_notebook.AddPage(self.generals_adv_panel, 'Generals in adv')
        # self.CreateStatusBar()
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(grid.EVT_GRID_COL_SIZE, self.on_size)

        self.main_notebook.Fit()
        self.SetMinSize(size=MY_SIZE)
        self.Fit()

    def on_size(self, event):
        width, height = self.GetClientSize()
        self.action_adv_panel.SetSize(width, height)
        self.action_adv_panel.table.SetColSize(1, width
                                               - sum(self.action_adv_panel.table.GetColSize(col) for col in (0, 2, 3))
                                               - self.action_adv_panel.table.GetRowLabelSize())
        self.main_notebook.SetSize(self.GetClientSize())


if __name__ == '__main__':
    app = wx.App()
    frame = Frame(None, sys.stdout)
    frame.Show(True)
    app.MainLoop()

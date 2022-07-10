import wx
import os
import logging
import my_types
import my_pygui
import cv2 as cv
from wx.lib.embeddedimage import PyEmbeddedImage

log = logging.getLogger(__name__)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.INFO)


class MyCanvas(wx.ScrolledWindow):
    def __init__(self, parent, id=-1, size=wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.ALWAYS_SHOW_SB)

        self.cursor_draw = None
        self.old_DC = None
        self.lines = []
        self.SetSize(1000, 1000)
        self.x = self.y = 0
        self.curLine = []
        self.cursorPosition = (0, 0)
        self.drawing = False
        self.dc = None
        self.reference = None
        self.step = None
        self.buffer = None
        self.overlay = wx.Overlay()

        self.SetBackgroundColour("TRANSPARENT")
        # self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))

        self.SetScrollRate(20, 20)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.leave_window)
        self.Bind(wx.EVT_ENTER_WINDOW, self.enter_window)
        # self.on_size()

    def on_size(self, event=None):
        logging.info('MyCanvas:on_size')
        # if event:
        #     event.Skip()

        if not self.buffer:
            x, y = self.GetSize()
            if x <= 0 or y <= 0:
                return

                # Initialize the buffer bitmap.  No real DC is needed at this point.

            self.buffer = wx.Bitmap(x, y)
        x, y = self.buffer.GetSize()

        # dc = wx.MemoryDC()
        # dc.SelectObject(self.buffer)
        # dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        # del dc

        self.SetScrollbars(10, 10, int(x/10), int(y/10))
        self.Refresh()

    # def getWidth(self):
    #     return self.size[0]
    #
    # def getHeight(self):
    #     return self.size[1]

    def OnPaint(self, event=None):
        logging.info('MyCanvas:OnPaint')
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  Since we don't need to draw anything else
        # here that's all there is to it.
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_VIRTUAL_AREA)

    # def draw_map(self):
    #     logging.info('MyCanvas:draw_map')
    #     self.size = self.adv_map.GetSize()
    #     self.SetScrollbars(10, 10, int(self.size[0] / 10), int(self.size[1] / 10))
    #     self.buffer = wx.Bitmap(*self.size)
    #     self.dc = wx.BufferedDC(None, self.buffer)
    #     self.dc.DrawBitmap(self.adv_map, 0, 0, True)

    # def draw_grid(self, locations=()):
    #     logging.info('MyCanvas:DoDrawing')
    #     # dc = wx.BufferedDC(None, self.buffer)
    #     # dc.DrawBitmap(self.adv_map, 0, 0, True)
    #
    #     # dc.SetFont(wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    #     # dc.SetTextForeground(wx.Colour(0xFF, 0x20, 0xFF))
    #     # te = dc.GetTextExtent("Hello World")
    #     # dc.DrawText("Hello World", 60, 65)
    #     #
    #     # dc.SetPen(wx.Pen('VIOLET', 4))
    #     # dc.DrawLine(5, 65 + te[1], 60 + te[0], 65 + te[1])
    #
    #     # lst = [(100, 110), (150, 110), (150, 160), (100, 160)]
    #     # dc.DrawLines(lst, -60)
    #     # dc.SetPen(wx.GREY_PEN)
    #     # dc.DrawPolygon(lst, 75)
    #     # dc.SetPen(wx.GREEN_PEN)
    #     # dc.DrawSpline(lst + [(100, 100)])
    #     dc = self.dc
    #     dc.SetBrush(wx.TRANSPARENT_BRUSH)
    #     dc.SetPen(wx.Pen('RED'))
    #     for loc in locations:
    #         dc.DrawCircle(loc.x, loc.y, 10)
    #
    #     # self.DrawSavedLines(dc)
    #     self.refresh_rect(dc)

    # def DrawSavedLines(self, dc):
    #     logging.info('MyCanvas:DrawSavedLines')
    #     dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
    #     for line in self.lines:
    #         for coords in line:
    #             dc.DrawLine(*coords)

    def SetXY(self, event):
        self.x, self.y = self.ConvertEventCoords(event)

    def ConvertEventCoords(self, event):
        return self.CalcUnscrolledPosition(event.GetX(), event.GetY())

    # def OnLeftButtonEvent(self, event):
    #     logging.info('MyCanvas:OnLeftButtonEvent')
    #     if self.IsAutoScrolling():
    #         self.StopAutoScrolling()
    #
    #     if event.LeftDown():
    #         logging.info('MyCanvas:OnLeftButtonEvent:LeftDown')
    #         self.SetFocus()
    #         self.SetXY(event)
    #         self.curLine = []
    #         self.CaptureMouse()
    #         self.drawing = True
    #
    #     elif event.Dragging() and self.drawing:
    #         logging.info('MyCanvas:OnLeftButtonEvent:Dragging')
    #         # In buffered drawing we'll just update the
    #         # buffer here and then refresh that portion of the
    #         # window.  Then the system will send an event and that
    #         # portion of the buffer will be redrawn in the
    #         # EVT_PAINT handler.
    #         dc = wx.BufferedDC(None, self.buffer)
    #
    #         dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))
    #         coords = (self.x, self.y) + self.ConvertEventCoords(event)
    #         self.curLine.append(coords)
    #         dc.DrawLine(*coords)
    #         self.SetXY(event)
    #
    #         self.refresh_rect(dc)
    #
    #     elif event.LeftUp() and self.drawing:
    #         logging.info('MyCanvas:OnLeftButtonEvent:LeftUp')
    #         self.lines.append(self.curLine)
    #         self.curLine = []
    #         self.ReleaseMouse()
    #         self.drawing = False

    def on_left_down(self, event=None):
        self.cursor_draw = True
        if not self.HasCapture():
            self.CaptureMouse()
        self.SetFocus()

    def on_left_up(self, event=None):
        self.cursor_draw = False
        if self.HasCapture():
            self.ReleaseMouse()
        bdc = wx.BufferedDC(None, self.buffer)
        if event:
            coords = self.ConvertEventCoords(event)
            bdc.DrawCircle(*(coords + (40,)))
            self.refresh_rect(bdc)

        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        del odc
        self.overlay.Reset()

    def leave_window(self, event):
        logging.info('MyCanvas:leave_window')
        self.cursor_draw = False
        if self.HasCapture():
            self.ReleaseMouse()
        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        del odc
        self.overlay.Reset()

    def enter_window(self, event):
        logging.info('MyCanvas:enter_window')
        self.cursor_draw = True
        if not self.HasCapture():
            self.CaptureMouse()
        self.SetFocus()

    def cursor_draw_switch(self, cursor_draw):
        return

    def on_mouse_move(self, event):
        if not self.cursor_draw:
            return
        logging.info('MyCanvas:on_mouse_move')
        if self.IsAutoScrolling():
            self.StopAutoScrolling()

        dc = wx.ClientDC(self)
        odc = wx.DCOverlay(self.overlay, dc)
        odc.Clear()
        # Mac's DC is already the same as a GCDC, and it causes
        # problems with the overlay if we try to use an actual
        # wx.GCDC so don't try it.  If you do not need to use a
        # semi-transparent background then you can leave this out.
        if 'wxMac' not in wx.PlatformInfo:
            dc = wx.GCDC(dc)

        coords = event.GetX(), event.GetY()
        if self.cursorPosition != coords:
            dc.SetPen(wx.BLUE_PEN)
            dc.SetBrush(wx.BLUE_BRUSH)
            dc.DrawCircle(*(coords + (40,)))
            self.cursorPosition = coords
        del odc

    def refresh_rect(self, dc):
        # figure out what part of the window to refresh, based
        # on what parts of the buffer we just updated
        x1, y1, x2, y2 = dc.GetBoundingBox()
        x1, y1 = self.CalcScrolledPosition(x1, y1)
        x2, y2 = self.CalcScrolledPosition(x2, y2)
        # make a rectangle
        rect = wx.Rect()
        rect.SetTopLeft((x1, y1))
        rect.SetBottomRight((x2, y2))
        rect.Inflate(2, 2)
        # refresh it
        self.RefreshRect(rect)


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.menu_bar_ids = {}
        self.menu_bar = None
        self.map_path = None

        # starting with an EmptyBitmap, the real one will get put there
        # by the call to .DisplayNext()
        # self.Canvas = MyCanvas(self, size=(500, 500))
        self.Canvas = None
        self.open_map_button = wx.Button(self, wx.ID_ANY, 'Open Map', size=(500, 500))

        # Using a Sizer to handle the layout: I never  use absolute positioning
        self.box = wx.BoxSizer(wx.VERTICAL)

        # adding stretchable space before and after centers the image.
        self.box.Add((1, 1), 0)
        # box.Add(self.Canvas, 1, wx.EXPAND)
        self.box.Add(self.open_map_button, 1, wx.EXPAND)
        self.box.Add((1, 1), 0)
        # self.Canvas.SetSizer(box)

        self.make_menu_bar()
        self.box.SetDimension(wx.DefaultPosition, (300, 300))
        self.SetSizerAndFit(self.box)
        self.Bind(wx.EVT_CLOSE, self.on_close_window)

    def on_close_window(self, event):
        self.Destroy()

    def make_menu_bar(self):
        logging.info('MainFrame:make_menu_bar:')
        self.menu_bar = wx.MenuBar()
        menu_f = wx.Menu()
        self.menu_bar_ids['open'] = wx.NewIdRef()
        menu_f.Append(self.menu_bar_ids['open'], '&Open')
        self.Bind(wx.EVT_MENU, self.open_map, id=self.menu_bar_ids['open'])
        self.menu_bar.Append(menu_f, '&File')

        menu_cursor_draw = wx.Menu()
        self.menu_bar_ids['cur_draw'] = wx.NewIdRef()
        menu_cursor_draw.AppendCheckItem(self.menu_bar_ids['cur_draw'], 'Find Flags')
        self.Bind(wx.EVT_MENU, self.cursor_draw_switch, id=self.menu_bar_ids['cur_draw'])
        self.menu_bar.Append(menu_cursor_draw, 'Start')

        self.SetMenuBar(self.menu_bar)

    def cursor_draw_switch(self, event=None):
        if self.menu_bar.IsChecked(self.menu_bar_ids["cur_draw"]):
            self.Canvas.cursor_draw_switch(True)
        else:
            self.Canvas.cursor_draw_switch(False)

    def calc_reference_coordinates(self, event):
        locations = my_pygui.locateAll('resource/flag_mini.png', self.map_path, confidence=0.95)

        locations.sort(key=lambda i: i.x)
        old_loc = 0
        dx_es = []
        for loc in locations:
            dx = loc.x - old_loc
            if dx != 0:
                old_loc = loc.x
                dx_es.append(dx)
        x = dx_es.pop(0)
        dx_average = sum(dx_es)/len(dx_es)

        locations.sort(key=lambda i: i.y)
        old_loc = 0
        dy_es = []
        for loc in locations:
            dy = loc.y - old_loc
            if dy != 0:
                old_loc = loc.y
                dy_es.append(dy)
        y = dy_es.pop(0)
        dy_average = sum(dy_es) / len(dy_es)
        self.Canvas.reference = my_types.Point(x, y)
        self.Canvas.step = my_types.Point(dx_average, dy_average)

    def open_map(self, event):
        logging.info('MainFrame:open_map')
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd() + '/data',
            defaultFile="",
            wildcard="Adventure file (*.png)|*.png",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.map_path = dlg.GetPath()
            adv_map = wx.Image(self.map_path, wx.BITMAP_TYPE_PNG)
            self.Canvas = MyCanvas(self, size=(500, 500))
            self.Canvas.buffer = wx.Bitmap(adv_map)
            self.box.Replace(self.open_map_button, self.Canvas)
            self.open_map_button.Destroy()
            self.Canvas.on_size()
            self.Layout()
            # self.Refresh()
            self.calc_reference_coordinates(event)

        dlg.Destroy()


class App(wx.App):
    def OnInit(self):
        frame = MainFrame(None, -1, "wxBitmap Test", wx.DefaultPosition, wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(frame)
        frame.Show(True)
        return True


if __name__ == "__main__":
    app = App(0)
    app.MainLoop()

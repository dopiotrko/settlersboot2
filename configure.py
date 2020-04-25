import pickle

import my_pygui
from listener import GetClick
from my_types import Point


class Configure:
    @staticmethod
    def run():

        coordinations = dict()
        get_click = GetClick()

        text = 'Star Menu'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['star'] = get_click.get()

        text = 'Adventures'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['adventures'] = get_click.get()

        text = 'Specialists'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['specialists'] = get_click.get()

        text = 'Search tex field'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['star_txt'] = get_click.get()

        text = 'Any General'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        get_click.get()

        text = 'Close General'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        get_click.get()

        text = 'Open same general by clicking him on the map (island)'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['center_ref'] = get_click.get()

        text = 'Recruit Up'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['r_up'] = get_click.get()
        region = (coordinations['r_up'] - Point(116, 46)).get() + (44, 44)
        loc = my_pygui.locateOnScreen('resource/army.png', region=region, confidence=.95)
        coordinations['recruit'] = Point.from_list(loc) + Point(74, 26)
        coordinations['bowmen'] = Point.from_list(loc) + Point(199, 26)
        coordinations['militia'] = Point.from_list(loc) + Point(324, 26)
        coordinations['cavalry'] = Point.from_list(loc) + Point(74, 81)
        coordinations['longbowman'] = Point.from_list(loc) + Point(199, 81)
        coordinations['soldier'] = Point.from_list(loc) + Point(324, 81)
        coordinations['crossbowman'] = Point.from_list(loc) + Point(74, 136)
        coordinations['elite_soldier'] = Point.from_list(loc) + Point(199, 136)
        coordinations['cannoneer'] = Point.from_list(loc) + Point(324, 136)

        text = 'Unload'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['unload'] = get_click.get()

        text = 'OK'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['confirm_army'] = get_click.get()

        text = 'Send'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['send'] = get_click.get()

        text = 'Cancel Send'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['send_cancel'] = get_click.get()
        coordinations['send_confirm'] = coordinations['send_cancel'] - Point(79, 0)

        text = 'Move'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['move'] = get_click.get()
        coordinations['attack'] = coordinations['move'] - Point(0, 86)

        text = 'Quest Book'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['book'] = get_click.get()
        coordinations['start_adventure'] = coordinations['book'] + Point(723, 585)

        text = 'Quest Book Down Arrow'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['book_down'] = get_click.get()

        with open('data/conf.dat', 'wb') as f:
            pickle.dump(coordinations, f)

        my_pygui.alert(text='End of configuration', title='Configuration', button='OK')


Configure().run()

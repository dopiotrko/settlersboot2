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

        text = 'Close Star Menu'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['star_close'] = get_click.get()

        my_pygui.alert(text='Open Star Menu again', title='Configuration', button='OK')
        get_click.get()

        text = 'Adventures'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['adventures'] = get_click.get()

        text = 'Specialists'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['specialists'] = get_click.get()

        my_pygui.alert(text='Open any explorer', title='Configuration', button='OK')
        get_click.get()

        text = 'Treasure'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        treasure_dict = dict()
        treasure_dict['open'] = get_click.get()

        text = 'Short treasure'
        my_pygui.alert(text=text, title='Configuration', button='OK')

        treasure_dict["short"] = get_click.get()
        treasure_dict["medium"] = treasure_dict["short"] + Point(171, 0)
        treasure_dict["long"] = treasure_dict["short"] + Point(0, 44)
        treasure_dict["very_long"] = treasure_dict["short"] + Point(171, 44)
        treasure_dict["longest"] = treasure_dict["short"] + Point(0, 88)
        treasure_dict["artefact"] = treasure_dict["short"] + Point(171, 88)
        treasure_dict["rare"] = treasure_dict["short"] + Point(0, 132)
        treasure_dict["confirm"] = treasure_dict["short"] + Point(-7, 240)
        coordinations['treasure'] = treasure_dict

        adventure_dict = dict()
        """open adv is in the same place as 'send to very long treasure' button"""
        adventure_dict['open'] = adventure_ref = treasure_dict["very_long"]
        adventure_dict["short"] = adventure_ref - Point(171, 0)
        adventure_dict["medium"] = adventure_ref
        adventure_dict["long"] = adventure_ref + Point(-171, 44)
        adventure_dict["very_long"] = adventure_ref + Point(0, 44)
        adventure_dict["confirm"] = adventure_ref + Point(-178, 152)
        coordinations['adventure'] = adventure_dict

        my_pygui.alert(text='Open Star Menu again', title='Configuration', button='OK')
        get_click.get()

        text = 'Search tex field'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['star_txt'] = get_click.get()

        text = 'First General'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['first_general'] = get_click.get()

        text = 'Close General'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['close_general'] = get_click.get()

        text = 'Open same general by clicking him on the map (island)'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['center_ref'] = get_click.get()

        text = 'Recruit Up'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['r_up'] = get_click.get()
        region = (coordinations['r_up'] - Point(116, 46)).get() + (44, 44)
        coordinations['first_army_region'] = region
        loc = my_pygui.locateOnScreen('resource/army.png', region=region, confidence=.95, center=False)
        coordinations['recruit'] = Point.from_point(loc) + Point(74, 26)
        coordinations['Swordsman'] = coordinations['recruit']
        coordinations['bowmen'] = Point.from_point(loc) + Point(199, 26)
        coordinations['Mounted Swordsman'] = coordinations['bowmen']
        coordinations['militia'] = Point.from_point(loc) + Point(324, 26)
        coordinations['Knight'] = coordinations['militia']
        coordinations['cavalry'] = Point.from_point(loc) + Point(74, 81)
        coordinations['Marksman'] = coordinations['cavalry']
        coordinations['longbowman'] = Point.from_point(loc) + Point(199, 81)
        coordinations['Amored Marksman'] = coordinations['longbowman']
        coordinations['soldier'] = Point.from_point(loc) + Point(324, 81)
        coordinations['Mounted Marksman'] = coordinations['soldier']
        coordinations['crossbowman'] = Point.from_point(loc) + Point(74, 135)
        coordinations['Besieger'] = coordinations['crossbowman']
        coordinations['elite_soldier'] = Point.from_point(loc) + Point(199, 135)
        coordinations['cannoneer'] = Point.from_point(loc) + Point(324, 135)
        coordinations['army_sum'] = Point.from_point(loc) + Point(0, -24)

        text = 'Unload'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['unload'] = get_click.get()

        text = 'OK'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['confirm_army'] = get_click.get()
        coordinations['elite'] = coordinations['confirm_army'] - Point(100, 0)

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
        coordinations['retreat'] = coordinations['move'] + Point(0, 43)

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

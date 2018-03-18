from traits.api import Trait, HasTraits, HasStrictTraits, Instance, \
                       List, Enum, Bool, Int, Str, Unicode, Float, \
                       File, Button, Range, TraitRange
from traitsui.api import View, Action, Handler, Item, UItem, Label, \
                   Spring, Group, HGroup, VGroup, VGrid, Tabbed, OKButton, OKCancelButtons, \
                   EnumEditor, TextEditor, CustomEditor

class TextEditor_vm(HasTraits):
    def __init__(self, text=''):
        self.Text = text
        
    Text = Str
    traits_view = View(Item(name = 'Text', show_label=False, 
                                 width=-500, height = -300, style = 'custom',
                                 editor = TextEditor(multi_line=True)),
                       buttons = OKCancelButtons,
                       kind = 'modal'
                      )

def test_TE():
    vm = TextEditor_vm()
    vm.configure_traits()
    print(vm.Text)   
    
test_TE()       
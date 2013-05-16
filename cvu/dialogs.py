#    (C) Roan LaPlante 2013 rlaplant@nmr.mgh.harvard.edu
#
#	 This file is part of cvu, the Connectome Visualization Utility.
#
#    cvu is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


from traits.api import (HasTraits,Bool,Event,File,Int,Str,Directory,Function,
	Enum,List,Button,Range,Instance)
from traitsui.api import (Handler,View,Item,OKCancelButtons,OKButton,Spring,
	Group,ListStrEditor,CheckListEditor,HSplit,FileEditor,VSplit,Action)
from traitsui.file_dialog import open_file
import os
import cvu_utils as util

class SubwindowHandler(Handler):
	def closed(self,info,is_ok):
		info.object.finished=is_ok
		info.object.notify=True

class InteractiveSubwindow(HasTraits):
	finished=Bool(False)
	notify=Event

def append_proper_buttons(button):
	#get around list mutability
	a=[button]
	a.extend(OKCancelButtons)
	return a

class OptionsWindow(InteractiveSubwindow):
	surface_visibility = Range(0.0,1.0,.15)
	circ_size = Range(7,20,10,mode='spinner')
	prune_modules = Bool(True)
	show_floating_text = Bool(True)
	intramodule_only = Bool(True)
	render_style=Enum('glass','cracked_glass','contours','wireframe','speckled')
	interhemi_conns_on = Bool(True)
	project_scalars = Bool(False)
	lh_conns_on = Bool(True)
	rh_conns_on = Bool(True)
	lh_nodes_on = Bool(True)
	rh_nodes_on = Bool(True)
	lh_surfs_on = Bool(True)
	rh_surfs_on = Bool(True)
	traits_view=View(
		VSplit(
			HSplit(
				Item(name='circ_size'),
				Item(name='show_floating_text',label='floating 3D text on'),
			),
			HSplit(
				Item(name='render_style',label='surface style'),
				Item(name='surface_visibility',label='surface opacity'),
			),
			HSplit(
				Item(name='prune_modules',label='prune singleton modules'),
			),
			HSplit(
				Item(name='intramodule_only',label='show intramodule connections only (when viewing modules)')
			),
			HSplit(
				Item(name='project_scalars',label='scalars project to surface'),
			),
			HSplit(
				Item(name='interhemi_conns_on',
					label='interhemispheric conns on'),
				Item(name='lh_conns_on',label='LH conns on'),
				Item(name='rh_conns_on',label='RH conns on'),
			),
			HSplit(
				Item(name='lh_nodes_on',label='LH nodes on'),
				Item(name='rh_nodes_on',label='RH nodes on'),
			),
			HSplit(
				Item(name='lh_surfs_on',label='LH surfaces on'),
				Item(name='rh_surfs_on',label='RH surfaces on'),
			),
			show_labels=False,
		),
		kind='live',buttons=OKCancelButtons,handler=SubwindowHandler(),
		title='Select your desired destiny',
	)

class RequireWindow(InteractiveSubwindow):
	require_ls=List(Str)
	please_note=Str('Enter the ROIs you would like to force to display on the '
		'circle plot.  You must spell them precisely, e.g. "lh_frontalpole"')
	traits_view=View(
		Item(name='please_note',style='readonly',height=35,width=250),
		Item(name='require_ls',editor=ListStrEditor(auto_add=True,
			editable=True),label='List ROIs here'),
		buttons=OKCancelButtons,title='Mango curry')

class AdjmatChooserWindowHandler(SubwindowHandler):
	def do_rw_show(self,info):
		info.object.require_window.edit_traits()

class AdjmatChooserWindow(InteractiveSubwindow):
	Please_note=Str("All but first field are optional.  Specify adjmat order "
		"if the desired display order differs from the existing matrix order."
		"  Specify unwanted channels as 'delete' in the label order.  Data "
		"field name applies to the data field for .mat matrices only.")
	adjmat=File
	open_adjmat=Button('Browse')
	#adjmat_order=Trait(None,None,File)
	adjmat_order=File
	max_edges=Int
	field_name=Str('adj_matrices')
	ignore_deletes=Bool
	require_window=Instance(InteractiveSubwindow,())
	RequireButton=Action(name='force display of ROIs',action='do_rw_show')
	traits_view=View(
		Item(name='Please_note',style='readonly',height=140,width=250),
		#HSplit(
		#	Item(name='adjmat',style='text'),
		#	Item(name='open_adjmat',show_label=False),
		#),
		Item(name='adjmat',),
		Item(name='adjmat_order',label='Label Order',),
		Item(name='max_edges',label='Max Edges'),
		Item(name='field_name',label='Data Field Name'),
		Item(name='ignore_deletes',label='Ignore deletes'),
		kind='live',buttons=append_proper_buttons(RequireButton),
		handler=AdjmatChooserWindowHandler(),
		title='Report all man-eating vultures to security',)

	def _open_adjmat_fired(self):
		self.adjmat=open_file()
	def _require_window_default(self):
		return RequireWindow()

class ParcellationChooserWindow(InteractiveSubwindow):
	Please_note=Str('Unless you are specifically interested in the'
		' morphology of an individual subject, it is recommended to use'
		' fsaverage5 and leave the first two fields alone.')
	SUBJECTS_DIR=Directory('./')
	SUBJECT=Str('fsavg5')
	labelnames_f=File
	open_labelnames_f=Button('Browse')
	parcellation_name=Str
	traits_view=View(
		Group(
			Item(name='Please_note',style='readonly',height=85,width=250),
			Item(name='SUBJECT'),
			Item(name='SUBJECTS_DIR'),
			Item(name='parcellation_name',label='Parcellation'),
			Item(name='labelnames_f',label='Label Display Order'),
			#HSplit(
			#	Item(name='labelnames_f',label='Label Display Order',
			#		style='text',springy=True),
			#	Item(name='open_labelnames_f',show_label=False)
			#),
		), kind='live',buttons=OKCancelButtons,handler=SubwindowHandler(),
			title="This should not be particularly convenient",)

	def _open_labelnames_f_fired(self):
		self.labelnames_f=open_file()

class LoadGeneralMatrixWindow(InteractiveSubwindow):
	Please_note=Str('Same rules for adjmat ordering files apply')
	mat=File
	open_mat=Button('Browse')
	mat_order=File
	field_name=Str
	ignore_deletes=Bool
	whichkind=Enum('modules','scalars')
	traits_view=View(
		Item(name='Please_note',style='readonly',height=50,width=250),
		Item(name='mat',label='Filename'),
		#HSplit(
		#	Item(name='mat',label='Filename',style='text',springy=True),
		#	Item(name='open_mat',show_label=False),
		#),
		#Item(name='mat',label='Filename',editor=FileEditor(entries=10),style='simple'),
		Item(name='mat_order',label='Ordering file'),
		Item(name='field_name',label='Data field name'),
		Item(name='ignore_deletes',label='Ignore deletes'),
		kind='live',buttons=OKCancelButtons,handler=SubwindowHandler(),
		title='Behold the awesome power of zombies')

	def _open_mat_fired(self):
		#self.mat=open_file()
		res=util.file_chooser(initialdir=os.path.dirname(self.mat),
			title='Roentgenium is very useful')
		if len(res)>0:
			self.mat=res
	
class NodeChooserWindow(InteractiveSubwindow):
	node_list=List(Str)
	cur_node=Int(-1)
	traits_view=View(
		Item(name='node_list',editor=
			ListStrEditor(selected_index='cur_node'),show_label=False),
		kind='live',height=350,width=350,buttons=OKCancelButtons,
		handler=SubwindowHandler(),
		resizable=True,title='Do you know the muffin man?')

class ModuleChooserWindow(InteractiveSubwindow):
	module_list=List(Str)
	cur_mod=Int(-1)
	traits_view=View(
		Item(name='module_list',editor=
			ListStrEditor(editable=True,selected_index='cur_mod'),show_label=False),
		kind='live',height=350,width=350,buttons=OKCancelButtons,
		handler=SubwindowHandler(),
		resizable=True,title='Roll d12 for dexterity check')

class ModuleCustomizerWindowHandler(SubwindowHandler):
	def do_clear(self,info):
		info.object.intermediate_node_list=[]

class ModuleCustomizerWindow(InteractiveSubwindow):
	initial_node_list=List(Str)
	intermediate_node_list=List(Str)
	return_module=List(Int)
	ClearButton=Action(name='Clear Selections',action='do_clear')
	traits_view=View(
		Item(name='intermediate_node_list',editor=CheckListEditor(
			name='initial_node_list',cols=2),show_label=False,style='custom'),
		kind='live',height=400,width=500,
		buttons=append_proper_buttons(ClearButton),
		handler=ModuleCustomizerWindowHandler(),
		resizable=True,scrollable=True,title='Mustard/Revolver/Conservatory')

	#index_convert may return a ValueError, it should be
	#contained in try/except from higher up.
	def index_convert(self):
		self.return_module=[self.initial_node_list.index(i)
			for i in self.intermediate_node_list]

class SaveSnapshotWindow(InteractiveSubwindow):
	savefile=Str(os.environ['HOME']+'/')
	dpi=Int(300)
	whichplot=Enum('3D brain','connection matrix','circle plot')
	traits_view=View(Group(
		Item(name='savefile'),
		Item(name='whichplot',label='view'),
		Item(name='dpi',label='dots per inch'),
	), kind='live',buttons=OKCancelButtons,handler=SubwindowHandler(),
		title="Help I'm a bug",height=250,width=250)

class MakeMovieWindow(InteractiveSubwindow):
	savefile=Str(os.environ['HOME']+'/')
	framerate=Int(20)
	bitrate=Int(4000) 
	samplerate=Int(8)
	#use x11grab exclusively.  remove snapshots altogether eventually
	type=Enum('x11grab','snapshots')
	anim_style=Bool(True)
	animrate=Int(8)
	traits_view=View(Group(
		Item(name='savefile'),
		Item(name='framerate',label='framerate'),
		Item(name='bitrate',label='bitrate (kb/s)'),
		#Item(name='type',label='movie making method'),
		Item(name='anim_style',label='automatically rotate'),
		Item(name='samplerate',label='animation speed'),
	), kind='live',buttons=OKCancelButtons,handler=SubwindowHandler(),
		title="Make me a sandwich",height=250,width=450)

class AnimatorHandler(Handler):
	finished=Instance(util.EventHolder)

	def __init__(self,finished):
		super(AnimatorHandler,self).__init__()
		self.finished=finished

	def closed(self,info,is_ok):
		self.finished.e=True

class ReallyOverwriteFileWindow(InteractiveSubwindow):
	Please_note=Str('That file exists.  Really overwrite?')
	save_continuation=Function # Continuation passing style
	traits_view=View(Spring(),
		Item(name='Please_note',style='readonly',height=25,width=250,
			show_label=False),
		Spring(),
		kind='live',buttons=OKCancelButtons,handler=SubwindowHandler(),
		title='Your doom awaits you')

class ErrorDialogWindow(HasTraits):
	message=Str
	traits_view=View(Item(name='error',style='readonly'),
		buttons=[OKButton],kind='nonmodal',height=150,width=300,
		title='Evil mutant zebras did this',)

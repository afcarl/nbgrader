from textwrap import dedent

from IPython.config.loader import Config
from IPython.utils.traitlets import Unicode, Bool, Dict, List
from IPython.nbconvert.preprocessors import ClearOutputPreprocessor

from nbgrader.apps.baseapp import (
    BaseNbConvertApp, nbconvert_aliases, nbconvert_flags)
from nbgrader.preprocessors import (
    IncludeHeaderFooter,
    ClearSolutions,
    LockCells,
    ComputeChecksums,
    SaveCells,
    CheckCellMetadata
)

aliases = {}
aliases.update(nbconvert_aliases)
aliases.update({
})

flags = {}
flags.update(nbconvert_flags)
flags.update({
    'no-db': (
        {'SaveCells': {'enabled': False}},
        "Do not save information about grade cells into the database."
    ),
    'create': (
        {'SaveCells': {'create_assignment': True}},
        "Create the assignment at runtime if it does not exist."
    )
})

class AssignApp(BaseNbConvertApp):

    name = Unicode(u'nbgrader-assign')
    description = Unicode(u'Prepare a student version of an assignment by removing solutions')

    aliases = Dict(aliases)
    flags = Dict(flags)

    examples = Unicode(dedent(
        """
        Running `nbgrader assign` on a file by itself will produce a student
        version of that file in the same directory. In this case, it will produce
        "Problem 1.nbconvert.ipynb":
        
        > nbgrader assign "Problem 1.ipynb"

        If you want to override the .nbconvert part of the filename, you can use
        the --output flag:

        > nbgrader assign "Problem 1.ipynb" --output "Problem 1.student.ipynb"

        Or, you can put the student version in a different directory. In the
        following example, there will be a file "student/Problem 1.ipynb" after
        running `nbgrader assign`:

        > nbgrader assign "Problem 1.ipynb" --build-dir=student

        You can also use shell globs, and copy files from one directory to another:

        > nbgrader assign teacher/*.ipynb --build-dir=student

        If you need to copy dependent files over as well, you can do this with
        the --files flag. In the following example, all the .jpg files in the 
        teacher/images/ folder will be linked to the student/images/ folder:

        > nbgrader assign teacher/*.ipynb --build-dir=student --files='["teacher/images/*.jpg"]'

        If you want to record the grade cells into the database (for use later
        when running `nbgrader autograde`), you can use the --save-cells flag.
        You will need to use this in combination with the --assignment flag to
        indicate what the assignment is that this notebook is a part of:

        > nbgrader assign "Problem 1.ipynb" --save-cells --assignment="Problem Set 1"

        You can additionally specifiy the database name with --db:

        > nbgrader assign "Problem 1.ipynb" --save-cells --assignment="Problem Set 1" --db=myclass

        """
    ))

    nbgrader_step_input = Unicode("source")
    nbgrader_step_output = Unicode("release")

    preprocessors = List([
        IncludeHeaderFooter,
        LockCells,
        ClearSolutions,
        ClearOutputPreprocessor,
        CheckCellMetadata,
        ComputeChecksums,
        SaveCells
    ])

    def _classes_default(self):
        classes = super(AssignApp, self)._classes_default()
        for pp in self.preprocessors:
            if len(pp.class_traits(config=True)) > 0:
                classes.append(pp)
        return classes

    def __init__(self, *args, **kwargs):
        super(AssignApp, self).__init__(*args, **kwargs)
        self.student_id = '.'

    def build_extra_config(self):
        self.extra_config = Config()
        self.extra_config.Exporter.default_preprocessors = self.preprocessors
        self.config.merge(self.extra_config)

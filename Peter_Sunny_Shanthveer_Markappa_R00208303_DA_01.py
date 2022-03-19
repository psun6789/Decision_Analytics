'''
Name : PETER SUNNY SHANTHVEER MARKAPPA
Student Id: R00208303
Subject: Decision Analytics
Assignment : 01
Submission Date : 18-March-2022
Draft : Task 1 -- Logical Puzzle
        Task 2 -- Sudoku
        Task 3 -- Project Planning
'''


import numpy as np
from ortools.sat.python import cp_model
import pandas as pd
import time

#-----------------------------------------------------------------------------------------------
#---------------------------------TASK 1--------------------------------------------------------
#-----------------------------------------------------------------------------------------------
def task_1_Logical_puzzle():
    names = ["James", "Daniel", "Emily", "Sophie"]

    starters = [
        "prawn-cocktail", "onion-soup",
        "mashroom-tart", "carpaccio"
    ]

    maincourse = [
        "baked-mackerel", "fried-chicken",
        "filet-steak", "vegan-pie"
    ]

    drinks = ["beer", "red-wine", "coke", "white-wine"]

    deserts = [
        "apple-crumble", "ice-cream",
        "chololate-cake", "tiramisu"
    ]

    gender = ["male", "female"]

    class SolutionPrinter(cp_model.CpSolverSolutionCallback):
        def __init__(self, starter, mc, drink, desert):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.starter_ = starter
            self.mc_ = mc
            self.drink_ = drink
            self.desert_ = desert
            self.solutions_ = 0

        def OnSolutionCallback(self):
            self.solutions_ = self.solutions_ + 1
            print("solution", self.solutions_)

            for name in names:
                print(" - " + name + ":")
                for starter in starters:
                    if (self.Value(self.starter_[name][starter])):
                        print("    - ", starter)
                for mc in maincourse:
                    if (self.Value(self.mc_[name][mc])):
                        print("    - ", mc)
                for drink in drinks:
                    if (self.Value(self.drink_[name][drink])):
                        print("    - ", drink)
                for desert in deserts:
                    if (self.Value(self.desert_[name][desert])):
                        print("    - ", desert)

            print()


    model = cp_model.CpModel()

    name_starter = {}
    for name in names:
        variables = {}
        for starter in starters:
            variables[starter] = model.NewBoolVar(name + starter)
        name_starter[name] = variables
    # print(peoplestarter)

    name_maincourse = {}
    for name in names:
        variables = {}
        for mc in maincourse:
            variables[mc] = model.NewBoolVar(name + mc)
        name_maincourse[name] = variables
    # print(peoplemaincourse)

    name_drink = {}
    for name in names:
        variables = {}
        for drink in drinks:
            variables[drink] = model.NewBoolVar(name + drink)
        name_drink[name] = variables
    # print(peopledrinks)

    name_desert = {}
    for name in names:
        variables = {}
        for desert in deserts:
            variables[desert] = model.NewBoolVar(name + desert)
        name_desert[name] = variables
    # print(peopledesert)


    # every person eats different menu items (starter, maincourse, drinks and desert)
    for i in range(4):
        for j in range(i+1, 4):
            for k in range(4):
                model.AddBoolOr([name_starter[names[i]][starters[k]].Not(), name_starter[names[j]][starters[k]].Not()])
                model.AddBoolOr([name_maincourse[names[i]][maincourse[k]].Not(), name_maincourse[names[j]][maincourse[k]].Not()])
                model.AddBoolOr([name_drink[names[i]][drinks[k]].Not(), name_drink[names[j]][drinks[k]].Not()])
                model.AddBoolOr([name_desert[names[i]][deserts[k]].Not(), name_desert[names[j]][deserts[k]].Not()])

    for name in names:
        # at least one food per person (starter, maincourse, drinks and desert)
        variables = []
        for starter in starters:
            variables.append(name_starter[name][starter])
        model.AddBoolOr(variables)

        variables = []
        for mc in maincourse:
            variables.append(name_maincourse[name][mc])
        model.AddBoolOr(variables)

        variables = []
        for drink in drinks:
            variables.append(name_drink[name][drink])
        model.AddBoolOr(variables)

        variables = []
        for desert in deserts:
            variables.append(name_desert[name][desert])
        model.AddBoolOr(variables)

        # max one food per person (starter, maincourse, drinks and desert)
        # means each person can choose only only item from each section (starter, maincourse, drinks and desert)
        for i in range(4):
            for j in range(i+1,4):
                model.AddBoolOr([
                        name_starter[name][starters[i]].Not(),
                        name_starter[name][starters[j]].Not()])
                model.AddBoolOr([
                        name_maincourse[name][maincourse[i]].Not(),
                        name_maincourse[name][maincourse[j]].Not()])
                model.AddBoolOr([
                        name_drink[name][drinks[i]].Not(),
                        name_drink[name][drinks[j]].Not()])
                model.AddBoolOr([
                        name_desert[name][deserts[i]].Not(),
                        name_desert[name][deserts[j]].Not()])


        #-----------------------------Conditions--------------------------------#

        #  condition 1
        # Emily does not each Prawn Cocktail in the starter and she also wont each Baked mackerel in main course menu
        model.AddBoolAnd([
            name_starter["Emily"]["prawn-cocktail"].Not(),
            name_maincourse["Emily"]["baked-mackerel"].Not()
        ])

        # Condition 2
        '''
        1) Daniel does not each Prawn cocktail in the starter
        2) James will not drink beer
            
            from this condition first statement it is confirmed that prawn cocktain is either eaten by
            Sophie or James
        # 
        '''
        model.AddBoolAnd([
            name_starter["Daniel"]["prawn-cocktail"].Not(),
            name_drink["James"]["beer"].Not()
        ])
        model.AddBoolOr([
            name_starter["Sophie"]["prawn-cocktail"],
            name_starter["James"]["prawn-cocktail"]
        ])

        # Condition 3
        """
            1) if Sophie does not eat prawn cocktail in the starter then only she will each fried-chicken in main course
            2) if sophie eats fried chicken then she wont eat prawn cocktail
            
            here 2 boolean And condition is applied for each dish 
        """
        model.AddBoolAnd([name_maincourse["Sophie"]["fried-chicken"]]).OnlyEnforceIf(
            name_starter["Sophie"]["prawn-cocktail"].Not())

        model.AddBoolAnd([name_starter["Sophie"]["prawn-cocktail"]]).OnlyEnforceIf(
            name_maincourse["Sophie"]["fried-chicken"].Not())


        # # Condition 4
        '''
            in this condition no specific name is mentioned therefore this condition is applied on all persons
            
            this condition states any person who eats filet-steak as main course then 
            that person must take onion-soup as starter and he/she has to eat apple crumble in the desert
        '''
        model.AddBoolAnd([
            name_starter[name]["onion-soup"],
            name_desert[name]["apple-crumble"]]).OnlyEnforceIf(name_maincourse[name]["filet-steak"])


        # condition 5
        '''
            this conditon also do not specify any specific name to it is applied on all four
            
            1) anyone who eats mashroom-tart in the starter menu he/she will drink red-wine
        '''
        model.AddBoolAnd([name_drink[name]["red-wine"]]).OnlyEnforceIf(name_starter[name]["mashroom-tart"])


        # Condition 6
        '''
        this statement can be divided into two parts
        1) person who eats ice-cream must not eat baked mackerel and visa-versa 
        2) person who eats vegan-pie in the main-course then he must not order prawn-cocktail or carpaccio in starter
        '''
        model.AddBoolAnd([
            name_maincourse[name]["baked-mackerel"].Not()]).OnlyEnforceIf(name_desert[name]["ice-cream"])

        model.AddBoolAnd([
            name_desert[name]["ice-cream"].Not()]).OnlyEnforceIf(name_maincourse[name]["baked-mackerel"])

        model.AddBoolAnd([
            name_starter[name]["carpaccio"].Not(),
            name_starter[name]["prawn-cocktail"].Not()]).OnlyEnforceIf(name_maincourse[name]["vegan-pie"])


        # # Condition 7
        '''
        from this statement we get to know that person who eats filet steak will drink beer or coke
        '''
        model.AddBoolOr([
            name_drink[name]["beer"],
            name_drink[name]["coke"]]).OnlyEnforceIf(name_maincourse[name]["filet-steak"])

        # # Condition 8
        '''
        from this statement we can understand that 
        1) only women will drink the wine if one drinks red other drinks white
        '''
        model.AddBoolAnd([
            name_drink["Emily"]["white-wine"]]).OnlyEnforceIf(name_drink["Sophie"]["red-wine"])

        model.AddBoolAnd([
            name_drink["Sophie"]["white-wine"]]).OnlyEnforceIf(name_drink["Emily"]["red-wine"])


        # # Condtition 9
        model.AddBoolOr([
            name_desert["James"]["chololate-cake"],
            name_desert["Daniel"]["chololate-cake"]
        ])

        model.AddBoolAnd([
            name_desert["James"]["chololate-cake"],
            name_drink["Daniel"]["coke"]]).OnlyEnforceIf(name_desert["Daniel"]["ice-cream"].Not())

        model.AddBoolAnd([
            name_desert["James"]["chololate-cake"],
            name_desert["Daniel"]["ice-cream"]]).OnlyEnforceIf(name_drink["Daniel"]["coke"].Not())


    solver = cp_model.CpSolver()
    status = solver.SearchForAllSolutions(model,
                                          SolutionPrinter(name_starter, name_maincourse, name_drink, name_desert))
    print((solver.StatusName(status)))

    if solver.StatusName(status) == "OPTIMAL":
        for name in names:
            if solver.Value(name_desert[name]['tiramisu']):
                print(name + " will have Tiramisu as Desert")











#-----------------------------------------------------------------------------------------------
#---------------------------------TASK 2--------------------------------------------------------
#-----------------------------------------------------------------------------------------------

def sudoku_task_2():
    #
    class SolutionPrinter(cp_model.CpSolverSolutionCallback):
        def __init__(self, sudokusize, sudokudict):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.solutions_, self.sudokuDict, self.sudokusize_ = 0, sudokudict, sudokusize


        def OnSolutionCallback(self):
            sudoku_solution = np.zeros((self.sudokusize_, self.sudokusize_)).astype(int)
            self.solutions_ += 1
            print("\nsolution", self.solutions_)

            row = 0
            while row<9:
                col = 0
                while col < 9:
                    sudoku_solution[row, col] = int(self.Value(self.sudokuDict[row, col]))
                    col +=1
                row+=1
            print(sudoku_solution)
    '''
        Given suduko grid in the Assignment PDF

                0   1   2   3   4   5   6   7   8
        -----------------------------------------------------
        0 -     *   *   *   *   *   *   *   3   *
        1 -     7   *   5   *   2   *   *   *   *
        2 -     *   9   *   *   *   *   4   *   *
        3 -     *   *   *   *   *   4   *   *   2
        4 -     *   5   9   6   *   *   *   *   8
        5 -     3   *   *   *   1   *   *   5   *
        6 -     5   7   *   *   6   *   1   *   *
        7 -     *   *   *   3   *   *   *   *   *
        8 -     6   *   *   4   *   *   *   *   5

    -----------------Star (*) represent the blank which has to be filled

    '''
    sudokuSize = 9
    smallgridSize = 3

    model = cp_model.CpModel()
    # We are creating and initializing the suduko grid of 9x9 with all the value '0'
    sudukoGrid = np.zeros((sudokuSize, sudokuSize), int)
    # print(sudukoGrid)

    # assigning the value to the position with referencing to Assignment pdf
    # first row
    sudukoGrid[0, 7] = 3
    # Second row
    sudukoGrid[1, 0],sudukoGrid[1, 2], sudukoGrid[1, 4] = 7, 5, 2
    # Third row
    sudukoGrid[2, 1], sudukoGrid[2, 6] = 9, 4
    # Fourth row
    sudukoGrid[3, 5],sudukoGrid[3, 8] = 4, 2
    # Fifth row
    sudukoGrid[4, 1], sudukoGrid[4, 2], sudukoGrid[4, 3], sudukoGrid[4, 8] = 5, 9, 6, 8
    # Sixth row
    sudukoGrid[5, 0], sudukoGrid[5, 4], sudukoGrid[5, 7] = 3, 1, 5
    # Seventh row
    sudukoGrid[6, 0], sudukoGrid[6, 1], sudukoGrid[6, 4], sudukoGrid[6, 6] = 5, 7, 6, 1
    # Eight Row
    sudukoGrid[7, 3] = 3
    # Ninth Row
    sudukoGrid[8, 0], sudukoGrid[8, 3], sudukoGrid[8, 8] = 6, 4, 5

    ##### Another way we can assign the suduko grid
    # # assigning the value to the position with referencing to Assignment pdf
    # sudukoGrid = [[0]*9 for i in range(9)]
    # sudukoGrid[0] = [0, 0, 0, 0, 0, 0, 0, 3, 0]
    # sudukoGrid[1] = [7, 0, 5, 0, 2, 0, 0, 0, 0]
    # sudukoGrid[2] = [0, 9, 0, 0, 0, 0, 4, 0, 0]
    # sudukoGrid[3] = [0, 0, 0, 0, 0, 4, 0, 0, 2]
    # sudukoGrid[4] = [0, 5, 9, 6, 0, 0, 0, 0, 8]
    # sudukoGrid[5] = [3, 0, 0, 0, 1, 0, 0, 5, 0]
    # sudukoGrid[6] = [5, 7, 0, 0, 6, 0, 1, 0, 0]
    # sudukoGrid[7] = [0, 0, 0, 3, 0, 0, 0, 0, 0]
    # sudukoGrid[8] = [6, 0, 0, 4, 0, 0, 0, 0, 5]


    # Let us see the Grid after Assigning the Value.. it has to match the grid of pdf
    print(sudukoGrid)

    # create dictionary where we can store the suduko value and the position number
    sudukoDict = {}
    #  here we are taking size as 9 because we have to create suduko of size 9
    key = 0
    while key < sudokuSize:
        val = 0
        while val < sudokuSize:
            sudukoDict[(key, val)] = sudukoGrid[key, val] if sudukoGrid[key, val] != 0 else model.NewIntVar(1, sudokuSize, 'sudukoDict[{},{}]'.format(key, val))
            val +=1
        key +=1

    # print(sudukoDict, "\n")

    '''
        now we have to put a constraint across all the rows
        using AddAllDifferent using OR tool
        loop through the row and each column and check the codition
        explanation of this is given in the pdf 
     '''
    # For each row we will traverse through the columns to put all different values
    [model.AddAllDifferent([sudukoDict[row, col] for col in range(sudokuSize)]) for row in range(sudokuSize)]
    # For each column we will traverse through the row to put all different values
    [model.AddAllDifferent([sudukoDict[row, col] for row in range(sudokuSize)]) for col in range(sudokuSize)]


    '''
        for this particular loop i have done reference of line no 80
        https://gist.github.com/ksurya/3940679
    '''
    # Constraint to have all different numbers within all the sub grids of sudoku grid
    row = 0
    while row < sudokuSize:
        col = 0
        while col < sudokuSize:
            model.AddAllDifferent([sudukoDict[row + i, j] for j in range(col, (col + smallgridSize)) for i in range(smallgridSize)])
            col += smallgridSize
        row += smallgridSize


    # print(sudukoDict)
    solver = cp_model.CpSolver()
    solver.SearchForAllSolutions(model, SolutionPrinter(sudokuSize, sudukoDict))


#-----------------------------------------------------------------------------------------------
#---------------------------------TASK 3--------------------------------------------------------
#-----------------------------------------------------------------------------------------------
def read_files():
    ''' read the sheets from the excel file and return the DF '''
    sheet1, sheet2, sheet3, sheet4 = 'Projects', 'Quotes', 'Dependencies', 'Value'
    column_index = 0
    projectsjobsDF = pd.read_excel(r'Assignment_DA_1_data.xlsx', sheet_name = sheet1, index_col=column_index)
    contractorquotesDF = pd.read_excel(r'Assignment_DA_1_data.xlsx', sheet_name=sheet2, index_col=column_index)
    projectdependenciesDF = pd.read_excel(r'Assignment_DA_1_data.xlsx', sheet_name=sheet3, index_col=column_index)
    projectvalueDF = pd.read_excel(r'Assignment_DA_1_data.xlsx', sheet_name=sheet4, index_col=column_index)
    return projectsjobsDF,contractorquotesDF, projectdependenciesDF, projectvalueDF


def task_3_project_planning():

    # Call the function to read the data
    projectsjobsDF,contractorquotesDF, projectdependenciesDF, projectvalueDF = read_files()


    class SolutionPrinter(cp_model.CpSolverSolutionCallback):

        def __init__(self, projects_taken, contractor_project_month, profit_):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.projects_taken_ = projects_taken
            self.contractor_project_month_ = contractor_project_month
            self.profit = profit_
            self.solutions_ = 0

        def OnSolutionCallback(self):
            self.solutions_ = self.solutions_ + 1
            print("\nsolution", self.solutions_)
            print("profit = ", self.Value(self.profit))

            for project in range(len(projectsjobsDF.index.tolist())):
                print(projectsjobsDF.index.tolist()[project], "  is Taken ") if (self.Value(self.projects_taken_[project])) else print(projectsjobsDF.index.tolist()[project], "  is Not Taken ")

                for month in range(len(projectsjobsDF.columns.tolist())):
                    for contractor in range(len(contractorquotesDF.index.tolist())):
                        if self.Value(self.contractor_project_month_[(project, month, contractor)]):
                            print(projectsjobsDF.loc[projectsjobsDF.index.tolist()[project]][projectsjobsDF.columns.tolist()[month]], "is done by ", contractorquotesDF.index.tolist()[contractor])
                            print("+++++++++++++++++++++++++++++++ \n")
            print()


    # CP model
    model = cp_model.CpModel()
    a, b = 1, 0
    # ______________________________________________________________________________________
    # __________________________________TASKS_______________________________________________
    # ______________________________________________________________________________________

    # _________ Task B_decision_for_contractors_working_of_projects_________________________

    contractor_skill = {}
    conind = contractorquotesDF.index
    for index in conind:
        qualification = [column for column in contractorquotesDF.columns if pd.notnull(contractorquotesDF.loc[index][column])]
        contractor_skill[index] = qualification
    # print("---------------------contractor_qualifaction-----------------")
    # print(contractor_qualifaction)

    #------------------ Whether to take project or not ----------------------
    projects_taken = {}
    project = 0
    while project < len(projectsjobsDF.index.tolist()):
        var = projectsjobsDF.index.tolist()[project].split(" ")[a]
        projects_taken[project] = model.NewBoolVar(var)
        project+=1
    # print("---------------------projects_taken-----------------")
    # print(projects_taken)


    # Decision variable if contractor is skilled then on which project he work considering all projects does not run all the year
    # Referred from the lab
    contractor_project_month = {}
    project = 0
    while project < len(projectsjobsDF.index.tolist()):
        month = 0
        while month < len(projectsjobsDF.columns.tolist()):
            contractor = 0
            while contractor < len(contractorquotesDF.index.tolist()):
                pmc = (project,month,contractor)
                var = 'project%i_month%i_contractor%i'
                contractor_project_month[pmc] = model.NewBoolVar(var%pmc)
                model.Add(contractor_project_month[pmc] == 0) if projectsjobsDF.loc[projectsjobsDF.index.tolist()[project]][projectsjobsDF.columns.tolist()
                [month]] not in contractor_skill[contractorquotesDF.index.tolist()[contractor]] else model.Add(contractor_project_month[pmc] <= 1)
                contractor+=1
            month+=1
        project+=1

    # task - C---- one contractor can work on only one project at same time
    contractor = 0
    while contractor < len(contractorquotesDF.index.tolist()):
        month = 0
        while month < len(projectsjobsDF.columns.tolist()):
            model.Add(sum( contractor_project_month[(project, month, contractor)] for project in range(len(projectsjobsDF.index.tolist())) ) <= a)
            month+=1
        contractor+=1
    # print("--contractor_project---")
    # print(contractor_project_month)


    # TAsk D ---- one contractor for one job for one the project if the project is taken
    project = 0
    while project < len(projectsjobsDF.index.tolist()):
        month = 0
        while month < len(projectsjobsDF.columns.tolist()):
            condition = pd.notnull(projectsjobsDF.loc[projectsjobsDF.index.tolist()[project]][projectsjobsDF.columns.tolist()[month]])
            if condition:
                model.Add(sum(contractor_project_month[(project, month, contractor)] for contractor in range(len(contractorquotesDF.index.tolist()))) == a ).OnlyEnforceIf(projects_taken[project])
            month +=1
        project+=1
    # print("--contractor_project---")
    # print(contractor_project_month)


    # TAsk E ----- no jobs will be assigned to contractors if project is not taken
    project = 0
    while project < len(projectsjobsDF.index.tolist()):
        month = 0
        while month < len(projectsjobsDF.columns.tolist()):
            model.Add(sum(contractor_project_month[(project, month, contractor)] for contractor in range(len(contractorquotesDF.index.tolist()))) == 0 ).OnlyEnforceIf(projects_taken[project].Not())
            month+=1
        project+=1
    # print("--contractor_project---")
    # print(contractor_project_month)


    # Task F --------- project Dependencicy
    # 1) required means the the dependent project has to be taken when indpendent is on
    # like project B can be taken when project A is taken
    # 2) of there is conflict then that particular project cannot be taken while another project is running
    dependencies_of_project = {}

    for rowproject in projectsjobsDF.index.tolist():
        var = {}
        for colproject in projectsjobsDF.index.tolist():
            var[colproject] = model.NewBoolVar("Dependencies_of_project_"+rowproject + " " + colproject)
        dependencies_of_project[rowproject] = var


    i = 0
    while i < len(projectsjobsDF.index.tolist()):
        j = 0
        while j < len(projectsjobsDF.index.tolist()):
            if projectdependenciesDF[projectsjobsDF.index.tolist()[i]][projectsjobsDF.index.tolist()[j]] == "required":
                model.AddBoolAnd([dependencies_of_project[projectsjobsDF.index.tolist()[i]][projectsjobsDF.index.tolist()[j]]])
            elif projectdependenciesDF[projectsjobsDF.index.tolist()[i]][projectsjobsDF.index.tolist()[j]] == "conflict":
                model.AddBoolAnd([dependencies_of_project[projectsjobsDF.index.tolist()[i]][projectsjobsDF.index.tolist()[j]].Not()])
            else:
                model.AddBoolOr([dependencies_of_project[projectsjobsDF.index.tolist()[i]][projectsjobsDF.index.tolist()[j]]])
            j+=1
        i+=1



    row = 0
    while row < len(projectsjobsDF.index.tolist()):
        col = 0
        while col < len(projectsjobsDF.index.tolist()):
            model.AddBoolAnd([projects_taken[row]]).OnlyEnforceIf([dependencies_of_project[projectsjobsDF.index.tolist()[row]] [projectsjobsDF.index.tolist()[col]]])
            col+=1
        row+=1

    # print("--dependencies_of_project---")
    # print(dependencies_of_project)


    #--- Task G --- Cost = 2160 condition checking

    cost_ = [projects_taken[i] * projectvalueDF['Value'].tolist()[i] for i in  range(b, len(projectsjobsDF.index.tolist()), a)]
    all_project_cost = sum(cost_)

    # print("Total")
    # print("all_project_cost = ", all_project_cost)

    cost = []
    project = 0
    while project < len(projectsjobsDF.index.tolist()):
        contractor = 0
        while contractor < len(contractorquotesDF.index.tolist()):
            month = 0
            while month < len(projectsjobsDF.columns.tolist()):
                condition1 = pd.notnull(projectsjobsDF.loc[projectsjobsDF.index.tolist()[project]][projectsjobsDF.columns.tolist()[month]])
                if condition1:
                    condition2 = pd.notnull(contractorquotesDF.loc[contractorquotesDF.index.tolist()[contractor]][str(projectsjobsDF.loc[projectsjobsDF.index.tolist()[project]][projectsjobsDF.columns.tolist()[month]])])
                    if condition2:
                        cost.append(contractor_project_month[(project, month, contractor)] * int(contractorquotesDF.loc[contractorquotesDF.index.tolist()[contractor]][str(projectsjobsDF.loc[projectsjobsDF.index.tolist()[project]][projectsjobsDF.columns.tolist()[month]])]))
                month+=1
            contractor += 1
        project+=1


    total_cost = sum(cost)

    # checking for the profit of 2160
    profit = all_project_cost - total_cost
    model.Add(profit >= 2160)

    profit_ = model.NewIntVar(0, sum(projectvalueDF['Value'].tolist()), 'profit_')
    model.Add(profit_ == profit)

    # task - H --- finding possible solution... in my case im getting 102 solutions
    solver = cp_model.CpSolver()
    solver.SearchForAllSolutions(model, SolutionPrinter(projects_taken, contractor_project_month, profit_))




def main():

    assignment_01_total_time_start = time.process_time()

    print("------------TASK 1 Logical Puzzle Start-----------------")
    ''' reference from the zebra puzzle solution given in Decision analytics Lab'''
    logical_puzzle_start_time = time.process_time()
    task_1_Logical_puzzle()
    logical_puzzle_end_time = time.process_time()
    print('Time Taken to complete Logical Puzzle {}'.format(logical_puzzle_end_time-logical_puzzle_start_time))
    print("------------TASK 1 Logical Puzzle End-----------------")


    print("------------TASK 2 SUDOKU Start-----------------")
    '''-----------reference https://opensourc.es/blog/sudoku/   ------------'''
    suduko_start_time = time.process_time()
    sudoku_task_2()
    suduko_end_time = time.process_time()
    print('Time Taken to complete Suduko {}'.format(suduko_end_time-suduko_start_time))
    print("------------TASK 2 SUDOKU End-----------------")


    print("------------TASK 3 Project Planning Start-----------------")
    '''... Reference ---- https://github.com/KarthikMurugadoss1804/Project-Planning---Constraint-programming/blob/master/ProjectPlanning.py---'''
    project_planning_start_time = time.process_time()
    task_3_project_planning()
    project_planning_end_time = time.process_time()
    print('Time Taken to complete the Project Planning Task : {}'.format(project_planning_end_time-project_planning_start_time))
    print("------------TASK 3 Project Planning End-----------------")

    assignment_01_total_time_end = time.process_time()
    print('Total Time Taken to complete all the 3 task : {}'.format(assignment_01_total_time_end-assignment_01_total_time_start))




if __name__ == "__main__":
    main()
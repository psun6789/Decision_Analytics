from ortools.linear_solver import pywraplp
# import itertools
import pandas as pd



def task1():

    '''Loading the Data...'''
    file_name = "Assignment_DA_2_Task_1_data.xlsx"
    sheet_1 = "Supplier stock"
    sheet_2 = "Raw material costs"
    sheet_3 = "Raw material shipping"
    sheet_4 = "Product requirements"
    sheet_5 = "Production capacity"
    sheet_6 = "Production cost"
    sheet_7 = "Customer demand"
    sheet_8 = "Shipping costs"

    ic = 0

    supplier_stock, raw_material_costs = pd.read_excel(file_name, sheet_name=sheet_1, index_col=ic), pd.read_excel(file_name, sheet_name=sheet_2, index_col=ic)
    raw_material_shipping, product_requirements = pd.read_excel(file_name, sheet_name=sheet_3, index_col=ic), pd.read_excel(file_name, sheet_name=sheet_4, index_col=ic)
    production_capacity, production_cost = pd.read_excel(file_name, sheet_name=sheet_5, index_col=ic), pd.read_excel(file_name, sheet_name=sheet_6, index_col=ic)
    customer_demand, shipping_costs = pd.read_excel(file_name, sheet_name=sheet_7, index_col=ic), pd.read_excel(file_name, sheet_name=sheet_8, index_col=ic)

    customer_demand, production_requirements = customer_demand.fillna(ic), product_requirements.fillna(ic)
    supplier_stock, production_capacity = supplier_stock.fillna(ic), production_capacity.fillna(ic)
    raw_material_costs, production_cost = raw_material_costs.fillna(ic), production_cost.fillna(ic)

    materials, factories, suppliers= list(raw_material_costs.columns), list(raw_material_shipping.columns), list(raw_material_costs.index)
    products, customers = list(product_requirements.index), list(customer_demand.columns)


    '''Creating Decision Variables'''

    solver = pywraplp.Solver('LPWrapper', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
    initialise = 0
    one = 1
    n_one = -1
    # B -- orders from factory to suppliers
    orders = {}
    production_volume = {}
    delivery = {}

    for f in factories:

        for m in materials:
            for s in suppliers:
                sol = solver.infinity()
                sol_1 = solver.NumVar(initialise, sol, f + "..." + m + "..." + s + "...")
                orders[(f,m,s)] = sol_1
    # print("Orders \n", orders)

        # B - each factory has its own capacity for production
        for p in products:
            sol = solver.infinity()
            sol_1 = solver.NumVar(initialise, sol, f + "...." + p)
            production_volume[(f, p)] = sol_1
    # print("Production Volume", production_volume)

        # B - Delivery to customers
        for c in customers:
            for p in products:
                sol = solver.infinity()
                sol_1 = solver.NumVar(initialise, sol, f + "...." + c + "...." + p)
                delivery[(f, c, p)] = sol_1
    # print("delivery", delivery)


    # # C - making sure that factory produces more than shippement
    for p in products:
        for f in factories:
            sol = solver.infinity()
            c = solver.Constraint(initialise, sol)
            c.SetCoefficient(production_volume[(f, p)], one)
            for cus in customers:
                c.SetCoefficient(delivery[(f, cus, p)], n_one)


    # D - customer demand has to be fulfilled
    for cus in customers:
        for pro in products:
            a = int(customer_demand.loc[pro][cus])
            c = solver.Constraint(a, a)
            for f in factories:
                c.SetCoefficient(delivery[(f, cus, pro)], one)

    # E - all the ordered items are in stock
    for s in suppliers:
        for m in materials:
            a = int(supplier_stock.loc[s][m])
            c = solver.Constraint(initialise, a)
            for factory in factories:
                c.SetCoefficient(orders[(factory, m, s)], one)


    # F - factories must purchase items to manifacture all the items

    cost = solver.Objective()

    for f in factories:
        for m in materials:
            sol = solver.infinity()
            c = solver.Constraint(initialise, sol)
            for s in suppliers:
                c.SetCoefficient(orders[(f, m, s)], one)
                for p in products:
                    pv = production_volume[(f, p)]
                    pr = production_requirements.loc[p][m]
                    c.SetCoefficient(pv, - pr)

        # G -
        for p in products:
            pc = int(production_capacity.loc[p][f])
            c = solver.Constraint(initialise, pc)
            pv = production_volume[(f, p)]
            c.SetCoefficient(pv, one)

        # H- objective function
        for s in suppliers:
            for m in materials:
                rmc = raw_material_costs.loc[s][m]
                rms =raw_material_shipping.loc[s][f]
                cost.SetCoefficient(orders[(f, m, s)], rmc + rms)

        for p in products:
            pc = int(production_cost.loc[p][f])
            pv = production_volume[(f, p)]
            cost.SetCoefficient(pv, pc)

        for c in customers:
            for p in products:
                sc = int(shipping_costs.loc[f][c])
                deli = delivery[(f, c, p)]
                cost.SetCoefficient(deli, sc)


    # I - solving linear programming to determine the overall optimal cost
    print("............. Solving Linear programming for optimal solution......................")

    cost.SetMinimization()
    status = solver.Solve()
    if status == solver.OPTIMAL:
        print("Optimal solution found")
        print("Overall Optimal cost: ", solver.Objective().Value(), "\n")
    else:
        print("Failed to find the optimal soltion")
        exit()


    for f in factories:
        for s in suppliers:
            fac_cost = initialise
            for m in materials:
                ord = orders[(f, m, s)].solution_value()
                print("\n", m, " = ", ord)
                rmc = raw_material_costs.loc[s][m]
                rmsc = raw_material_shipping.loc[s][f]
                ord = orders[(f, m, s)].solution_value()
                fac_cost += ord * rmc
                fac_cost += ord * rmsc
            if fac_cost:
                print(" for ", s, " factory = ", fac_cost)

        # L - manifacturing cost of each factory
        pct = initialise
        for p in products:
            pv = production_volume[(f, p)].solution_value()
            if pv > initialise:
                print(f, "produces ", p, ": ", pv)
                pc = production_cost.loc[p][f]
                pct += pv * pc
        if pct:
            print("Manufacturing cost: ", int(pct))


    # M -- to determine how much items are shipped to each customers
    # also determining the total shipping cost
    print("----------------TASK M--------------")
    print("Total Shipping Cost:")

    for c in customers:
        ship_cost = initialise
        print("for ", c)
        for p in products:
            print(p, "Has been Delivered")
            for f in factories:
                deli = delivery[(f, c, p)].solution_value()
                print("\t", f, ": ", deli)
                sc = shipping_costs.loc[f][c]
                ship_cost += deli * sc
        if ship_cost:
            print("   Shipping Cost: ", ship_cost, "\n\n")

        # # N --
        print("for", c, "\n")
        for p in products:
            unit_cost = initialise
            if int(customer_demand.loc[p][c]) > initialise:
                print("for  ", p, "\n")
                for f in factories:
                    deli = delivery[(f, c, p)].solution_value()
                    if deli > initialise:
                        print("from", f, "\n")

                        sc = shipping_costs.loc[f][c]
                        transportation_cost = deli * sc

                        pc = production_cost.loc[p][f]
                        man_cost = deli * pc
                        unit_cost += transportation_cost
                        unit_cost += man_cost

                        for m in materials:
                            units_materials, cost_of_materials, counts_of_materials, r_trans_cost = initialise, initialise, initialise, initialise
                            pr = product_requirements.loc[p][m]
                            units_materials += deli * pr

                            print("\t  ", m, ": ", units_materials)
                            for s in suppliers:
                                ord_ = orders[(f, m, s)].solution_value()
                                rmc = raw_material_costs.loc[s][m]
                                rmsc = raw_material_shipping.loc[s][f]
                                cost_of_materials += ord_ * rmc
                                r_trans_cost += ord_ * rmsc

                                counts_of_materials += ord_
                            material_cost_to_customer = ((cost_of_materials + r_trans_cost) / counts_of_materials) * units_materials
                            unit_cost += material_cost_to_customer
                solu_ = unit_cost / int(customer_demand.loc[p][c])
                print("\t item cost per unit : ", solu_)





if __name__ == "__main__":
    task1()

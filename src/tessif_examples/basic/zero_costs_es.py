# src/tessif_examples/zero_costs_es.py
"""Tessif minimum working example energy system model."""
import numpy as np
import pandas as pd
import tessif.namedtuples as nts
from pandas import date_range
from tessif.model import components, energy_system


def create_zero_costs_es(directory=None, filename=None):
    """
    Create a small energy system having to costs alocated to commitment
    and expansion, but a low emission consttaint.

    Interesting about this example is the fact that there are many possible
    solutions, so solver ambiguity might be observed using this es. This
    energy system also serves as a method of validation for the post processing
    capabilities, to handle 0 costs in case of scaling results to maximum
    occuring costs.


    Return
    ------
    es: :class:`tessif.model.energy_system.AbstractEnergySystem`
        Tessif energy system.

    References
    ----------
    :ref:`Models_Tessif_mwe` - For a step by step explanation on how to create
    a Tessif energy system.

    Examples
    --------
    Use :func:`create_zero_costs_es` to quickly access a tessif
    energy system to use for doctesting, or trying out this framework's
    utilities.

    (For a step by step explanation see :ref:`Models_Tessif_mwe`):

        import tessif.examples.data.tsf.py_hard as tsf_py
        es = tsf_py.create_zero_costs_es()

        for node in es.nodes:
            print(str(node.uid))
        Powerline
        Emitting Source
        Capped Renewable
        Uncapped Renewable
        Demand

    Visualize the energy system for better understanding what the output means:

        from tessif-visualize import dcgraph as dcv

        app = dcv.draw_generic_graph(
            energy_system=create_zero_costs_es(),
            color_group={
                'Powerline': '#009900',
                'Emitting Source': '#cc0033',
                'Demand': '#00ccff',
                'Capped Renewable': '#ffD700',
                'Uncapped Renewable': '#ffD700',},
            },
        )

        # Serve interactive drawing to http://127.0.0.1:8050/
        app.run_server(debug=False)

    .. image:: ../images/zero_costs_example.png
        :align: center
        :alt: Image showing the zero costs example energy system graph.
    """

    # 2. Create a simulation time frame of 2 one hour time steps as a
    # :class:`pandas.DatetimeIndex`:
    timeframe = pd.date_range("7/13/1990", periods=4, freq="H")

    # 3. Creating the individual energy system components:
    # emitting source having no costs and no flow constraints but emissions
    emitting_source = components.Source(
        name="Emitting Source",
        outputs=("electricity",),
        # Minimum number of arguments required
        flow_emissions={"electricity": 1},
    )

    # capped source having no costs, no emission, no flow constraints
    # but existing and max installed capacity (for expansion) as well
    # as expansion costs
    capped_renewable = components.Source(
        name="Capped Renewable",
        outputs=("electricity",),
        # Minimum number of arguments required
        flow_rates={"electricity": nts.MinMax(min=0, max=2)},
        expandable={"electricity": True},
        expansion_limits={"electricity": nts.MinMax(min=2, max=4)},
    )

    # uncapped source having no costs and no emissions
    # and an externally set timeseries as well as expansion costs
    uncapped_min, uncapped_max = [1, 2, 3, 1], [1, 2, 3, 1]

    uncapped_renewable = components.Source(
        name="Uncapped Renewable",
        outputs=("electricity",),
        # Minimum number of arguments required
        flow_rates={"electricity": nts.MinMax(min=0, max=1)},
        expandable={"electricity": True},
        timeseries={"electricity": nts.MinMax(min=uncapped_min, max=uncapped_max)},
        expansion_limits={
            "electricity": nts.MinMax(
                min=max(uncapped_max),
                max=float("+inf"),
            )
        },
    )

    electricity_line = components.Bus(
        name="Powerline",
        inputs=(
            "Emitting Source.electricity",
            "Capped Renewable.electricity",
            "Uncapped Renewable.electricity",
        ),
        outputs=("Demand.electricity",),
        # Minimum number of arguments required
    )

    demand = components.Sink(
        name="Demand",
        inputs=("electricity",),
        # Minimum number of arguments required
        flow_rates={"electricity": nts.MinMax(min=10, max=10)},
    )

    global_constraints = {"emissions": 8}

    # 4. Creating the actual energy system:
    explicit_es = energy_system.AbstractEnergySystem(
        uid="Zero Costs Example",
        busses=(electricity_line,),
        sinks=(demand,),
        sources=(
            emitting_source,
            capped_renewable,
            uncapped_renewable,
        ),
        timeframe=timeframe,
        global_constraints=global_constraints,
    )

    return explicit_es
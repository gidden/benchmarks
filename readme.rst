Benchmark Repository
====================

This is a repository for the specification of benchmarks, a 
database of recipes used in benchmarks, and scripts to translate the 
specifications and recipes into Cyclus input files.

Specification Format
--------------------

The fuel cycle simulation benchmark input specification format is described in
detail below. The specification is split into three sections: materials,
describing the materials to be used in the simulation; facilities, describing
the facilities that will act in the simulation; and fuel cycle, describing the
behavior of the fuel cycle during the simulation (e.g., when certain types of
facilities become available). Each section includes an optional metadata
structure. The purpose of this structure is to provide additional information,
including simulator-specific information. A classic example is that of fuel
assembly geometry, described in [BOUCHER07]_, which could be included in the
metadata of a reactor facility. In general, we try to prescribe to the examples
laid forth in other specification languages in computational nuclear science
(e.g. [MATTOON12]_). We are additionally guided by this work when arbitrary
decisions must be made, e.g., using camelCase instead of other ways to write
compound_words.

Materials
+++++++++

A 'materials specification' defines the isotopic makeup of material in a fuel
cycle simulation. For the purposes of benchmarks, isotopic definitions generally
come in two flavors: prescribed recipes or process-defined isotopic vectors. A
predefined recipes is straightforward, and an example of this is unirradiated
uranium. Natural uranium's isotopics are well known (within deviations in
natural abundances), and the enrichment process can be modeled with simple
analytical equations. Accordingly, precise isotopic recipes can be provided for
such materials. During and after irradiation, however, complex physical models
are required to obtain precise isotopic compositions; the current best practice
for the majority of models is to perform such calculations offline (i.e., not
within a simulation). Accordingly, certain factual statements can be made based
on domain-level knowledge to place restrictions or constraints on a defined
material, but precisely defining the isotopic makeup of material
post-irradiation is generally not applicable.

We define the materials specification as follows: ::

   * materials
     * materialName1
       * metadata (optional)
       * attributes
      	 * recipe
           * true/false
      	 * suggestedComposition (optional)
           * isotope1
           * isotope2
         * parents (optional)
       * constraints
       	 * constraint1
       	 * constraint2...
     * materialName2...

This specifications covers both cases described above. If a material is
process-defined (i.e., it is not a recipe), the suggestedComposition structure
allows for the benchmark to provide a "hint" as to what the processed
composition might be. Such a structure covers the majority of benchmark cases
where single-burnup compositions are provided, e.g. 45 GWd/tHM UOX. 

The constraints section provides requirements that materials must meet. If the
material can be described as a recipe, then isotope-isotopic fraction pairs
(i.e., strict equality constraints) can be provided to fully specify the
material. If the material is process-defined, then inequalities can be used to
define the material. Density, or any other material property, is specified in
the constraints section. 

The parents field allows for related materials to be specified in a more compact
manner. Any child materials incorporate both their prescribed constraints as
well as the constraints of their parents. 

Two examples of the material specification implemented in JSON are provided
below ::

      "leu": {
          "attributes": {
              "recipe": true
          }
          "constraints": [      
              ["U235", 0.0495],
              ["U238", 0.9505],
              ["O16", 2.0],
              ["density", 10.2]
          ]
      },
      "spent_pwr_uox": {
          "attributes": {
              "recipe": false,
              "suggestedComposition": [
                  ["U235",0.01],
                  ...
              ]
          }
          "constraints": [
              "id == 92235 && x < 0.0495",
              "id == 92238 && x < 0.9505",
              "density < 10.2"
          ]
      }

Facilities
++++++++++

A 'facility specification' provides a minimal definition to determine the
working behavior of facilities, e.g. reactors and separations facilities, in a
simulation. There are members of the specification common to all facilities,
including a classification (i.e., type), a name, a lifetime, and input and
output materials. Of course, different facilities are defined by different
parameters, so each class of facility must have a unique
specification. Presented herein is a proof-of-principle draft with suggestions
for how to specify certain facilities. It is not exhaustive, and comments and
suggestions for improvements are certainly welcome.

In general, the specification provides a description of each parameter (i.e.,
its units) in the attributes section and a definition of each parameter (i.e.,
its value) in the constraints section.

For completeness, the facility specification section is defined as follows: ::

   * facilities
     * facilitySpecification1
     * facilitySpecification2...

The exact facility specification depends on the class of facility. The selected
facilities specifications which are supported at the present time are described
below.

Reactors
~~~~~~~~

The current specification assumes that reactors have defined core fuel zones. In
the simplest case, e.g. a UOX LWR, there may be one zone. A more complicated
case would include a fast reactor that incorporates an axial and radial
blanket. 

.. Anthony, it appears that the attributes section is really the specification
   definition. If you make the analogy to the GND paper, our attributes for
   facilities (and only facilities) outline what will come next, which is
   basically the specification definition.. To clarify, is the attributes
   section only for units?

We define the reactor specification as follows: ::

   * reactorName1
     * metadata (optional)
       * type: reactor
     * attributes
       * thermalPower: units
       * efficiency: units
       * cycleLegth: units
       * batches: units
       * lifetime: {units | distributed} 
       * fuels:
	 * fuel1
	   * coreLoading: units
	   * burnup: units
	   * coolingTime: units
	   * storageTime: units
	 * fuel2... (optional)
     * constraints
       * thermalPower: value
       * efficiency: value
       * cycleLegth: value
       * batches: value
       * lifetime: {value | distributed}
       * fuels:
	 * fuel1
	   * coreLoading: value
	   * burnup: value
	   * coolingTime: value
	   * storageTime: value
	 * fuel2... (optional)
     * inputMaterials
     * outputMaterials
   * reactorName2...

In this specification, the units member is a pair of values stating the data
type and units, for example::

  thermalPower: float, GWd/tHM

The lifetime member allows for one of two types of values. If specific units and
a value are given, then all facilities of the given class are assigned a
specific lifetime. If it instead flagged as a distribution, facility lifetimes
are inferred from the Fuel Cycle demand section. This is required of the
specification for now due to the method by which previous benchmarks have been
defined (i.e., defining a "facility life distribution curve" rather than
defining a demand for certain facilities -- see [BOUCHER07]_).

.. Anthony, can you advise here (yea, nay)?

An example of the specification implemented in JSON is shown below: ::

     "lwr_reactor": {
     	 "metadata: {
	     "type":"reactor"
	 }
	 "attributes": {
	     "thermalPower": ["float", "GWt"],
	     "efficiency": ["float", "percent"],
	     "cycleLength": ["int", "month"],
	     "batches": ["int",None],
	     "lifetime": ["int", "year"],
	     "fuels": {
	         "leu": {
	     	     "coreLoading": ["float", "kg"],
		     "burnup": ["float", "GWd/tHM"],
	     	     "storageTime": ["int", "year"],
	     	     "coolingTime": ["int", "year"],
		 }
	     }
	 },
	 "constraints": [
	     ["thermal_power", 4.25],
	     ["efficiency", 34.1],
	     ["cycle_length", 12],
	     ["core_loading", 78.7],
	     ["nbatches", 3],
	     ["lifetime", 60],
	     "fuels": {
	         "leu": {
	     	     ["coreLoading", 78.7],
	     	     ["burnup", 60],
	     	     ["storageTime", 2],
	     	     ["coolingTime", 5],
		 }
	     }
	 ],
	 "inputs": ["leu"],
	 "outputs": ["used_leu"]
     }

.. Anthony, can you confirm that the reason we use dictionaries above is that we
   have multiple entries per "key" versus below where it is known that we'll
   only have one entry per "key"? I'm curious because of the "fuels" data
   structure I've introduced


Repositories
~~~~~~~~~~~~

Repositories serve mostly as sinks for certain types of materials. Additional
fidelity can be provided by asserting a limit on the quantity or quality
(e.g. radiotoxicity or thermal heat load) of the entering materials. Accordingly,
a repository is specified as follows: ::

   * repositoryName1
     * metadata (optional)
       * type: repository
     * attributes
       * capacity: units
       * lifetime: units
     * constraints
       * capacity: value
       * lifetime: value
     * inputMaterials
   * repositoryName2...

An example of a specification implemented in JSON is shown below: ::

     "lwr_repository": {
     	 "metadata: {
	     "type":"repository"
	 }
	 "attributes": {
	     "lifetime": ["int", "year"], 
	     "capacity": ["double", "tHM/year"]
	 }
	 "constraints": {
	     "lifetime": 60, 
             "capacity": 800.0
	 }, 
	 "inputs": ["used_leu"]
      }

Reprocessing
~~~~~~~~~~~~

Reprocessing plants are generally used in a simulation to recycle certain
elemental groups to be reused as fuel, separating valuable, fissile isotopes
(and their elemental family), from neutron poison isotopes. Accordingly,
reprocessing plants must specify some number of elemental families and a
corresponding separation efficiency. Furthermore, the facility is defined by a
processing capacity and the temporal nature of the separations process is
captured in a processing time member. A reprocessing facility is specified as
follows: ::

   * reprocessingName1
     * metadata (optional)
     * attributes
       * capacityType: units
       * lifetime: units
       * separationClasses:
         * class1:
	   * efficiency: units
	 * class2...
     * constraints
       * capacityType: value
       * lifetime: value
       * separationClasses:
         * class1:
	   * efficiency: value
	   * constitutents: values
	 * class2...
     * inputMaterials
     * outputMaterials
   * repositoryName2...

.. Anthony, can you advise on how the separationClasses structure fits with your
   ideas here.. I'm still reallly struggling to understand when to use
   dictionaries and lists and when to declare things in the attributes section
   and when to declare them in constraints

Advanced Fabrication
~~~~~~~~~~~~~~~~~~~~

Fabrication of advanced fuels, i.e., those using some amount of recycled
material is required to model advanced fuel cycles. These fabrication facilities
generally take some set of input separated elements and a filling fertile
material (e.g. natural or depleted uranium), and output one or more advanced
fuel types. The decision making algorithm of how much of each constituent to
send to the facility and how to construct a given fuel type is generally
simulation-engine specific. One can, however, specify connections and capacities
as has been done in prior sections. An advanced fabrication facility is
specified as follows: ::

   * fabricatorName1
     * metadata (optional)
     * attributes
       * capacities
         * capacityType1: units
         * capacityType2: units
	 * ...
       * lifetime: units
     * constraints
       * capacities
         * capacityType1: value
         * capacityType2: value
	 * ...
       * lifetime: value
     * inputMaterials
     * outputMaterials
   * fabricatorName2...

Fuel Cycle
++++++++++

A 'fuel cycle specification' defines the basic progression and facility
availability of a simulation. These parameters include the time period to be
simulated, the initial condition of the simulation, the growth of facilities
(i.e., the demand for such facilities), and the technological availability of
certain advanced facilities.

We define the fuel cycle specification as follows: ::
  
  * fuelCycle
    * metadata (optional)
    * attributes
      * grid: units
      * initialConditions:
	* facility1: number
	* facility2...
      * demands:
	* demand1: units, facilities
	* demand2...
    * constraints
      * grid: value
      * demands:
        * demand1: 
          * grid: value
	  * growth: description
        * demand2...

In general, the attributes and constraints of the fuelCycle data structure are
pretty straightforward. Inclusive time periods as described as grids,
e.g. [0,100] describes a time period between 0 and 100 in a given unit. Facility
growth curves are described via demand data structures. Demand data structures
contain two state attributes, their units and the facilities that meet the given
demand. They are constrained by the time periods over which they span and the
description of their growth. Growth descriptors essentially describe piece-wise
functions. An example of a a linear piece-wise growth descriptor is specified as
follows: ::
  
  * growth:
    * type: linear
    * period: 
      * startTime: value
      * startValue: value (optional)
      * slope: value

The period structure describes each piece-wise section of the growth function. A
starting value can be supplied if required.

An example implementation of the fuel cycle specification in JSON is given
below::

 "fuelCycle": {
     "attributes": {
         "grid": "year",
	 "initialConditions": {
	     "repository": 1,
	 },
	 "demands": {
	     "power": ["GWe", ["lwrReactor"]]
	 }
     }
     "constraints": {
         "grid": [0, 120],
         "demands": {
	     "power": {
	         "grid": [0,120],
	         "growth": {
		     "type": "linear",
		     "period": {
		         "startTime": 0,
		         "startValue": 1000,
	                 "slope": 500
		     }
                 }
	     }
	 }
     }
 }

Citations
---------

.. [BOUCHER07] L. BOUCHER, “Specification for the Benchmark Devoted to Scenario
	       Codes,” Tech. Rep. NEA/NSC/DOC(2007)13/REV1, OECD, Nuclear Energy
	       Agency (Mar. 2008).

.. [MATTOON12] C. M. MATTOON, B. R. BECK, N. R. PATEL, N. C. SUM-
	       MERS, G. W. HEDSTROM, and D. A. BROWN, “Gener- alized Nuclear
	       Data: A New Structure (with Supporting Infrastructure) for
	       Handling Nuclear Data,” Nuclear Data Sheets, 113, 12, 3145 – 3171
	       (2012).

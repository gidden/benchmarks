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
facilities become available). 

Materials
+++++++++

A 'materials specification' defines the isotopic makeup of material in a fuel
cycle simulation. For the purposes of benchmarks, isotopic definitions generally
come in two flavors: predescribed recipes or process-defined isotopic vectors. A
predefined recipes is straightforward, and an example of this is unirradiated
uranium. Natural uranium's isotopics are well known (within deviations in
natural abundancies), and the enrichment process can be modeled with simple
analytical equations. Accordingly, precise isotopic recipes can be provided for
such materials. During and after irradiation, however, complex physical models
are required to obtain precies isotopic compositions; the current best practice
for the majority of models is to perform such calculations offline (i.e., not
within a simulation). Accordingly, certain factual statements can be made based
on domain-level knowledge to place restrictions or constraints on a defined
material, but precisely defining the isotopic makeup of material
post-irradiation is generally not applicable.

We define the materials specification as follows: ::

   * materials
     * materialName1
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
manner. Any child materials incorporate both their prescriped constraints as
well as the constraints of their parents. 

Two example of specified materials are provided below ::

  {"materials": {
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
     * attributes
       * thermalPower: units
       * efficiency: units
       * cycleLegth: units
       * batches: units
       * lifetime: units
       * fuels:
	 * fuel1
	   * coreLoading: units
	   * burnup: units
	   * coolingTime: units
	   * storageTime: units
	 * fuel2... (optional)
     * constriants
       * thermalPower: value
       * efficiency: value
       * cycleLegth: value
       * batches: value
       * lifetime: value
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

Repositories
~~~~~~~~~~~~

Repositories serve mostly as sinks for certain types of materials. Additional
fidelity can be provided by asserting a limit on the quantity or quality
(e.g. radiotoxicity or thermal heatload) of the entering materials. Accordingly,
a repository is specified as follows: ::

   * repositoryName1
     * attributes
       * capacityType: units
       * lifetime: units
     * constriants
       * capacityType: value
       * lifetime: value
     * inputMaterials
   * repositoryName2...


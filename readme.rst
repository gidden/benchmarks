Benchmark Repository
====================

This is a repository for the specification of benchmarks, a 
database of recipes used in benchmarks, and scripts to translate the 
specifications and recipes into Cyclus input files.

Specification Format
--------------------

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
     * material1
       * attributes
      	 * recipe
           * true/false
      	 * suggestedComposition (optional)
           * isotope1
           * isotope2
       * constraints
       	 * constraint1
       	 * constraint2...
       * parents (optional)
     * material2...

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

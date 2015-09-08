
getAllbyArc("bdd_projet", function(projects){
    console.log(projects.length);

    for (var i = 0; i < projects.length; i++) {
        var project = projects[i];

        var clean = replaceObjectsByID(these.meta);
         
                ID : project.ID,
                permalink : project.link,
                

    }
})

function replaceObjectsByID (these) {

    var these_fields  = ["nom_des_porteurs", "chercheur", "partenaires", "laboratoire" ,"etablissements_gestionnaires"];

    these_fields.forEach(function(field){
        var toParse = these["these-"+field] || [];

        these[field] = toParse.map(function(d){ return d.ID })
        delete these["these-"+field]
    })

    return these;
}

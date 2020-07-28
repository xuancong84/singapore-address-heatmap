// Map-highlighter library, requires "leaflet.js"

function drawElement(draw_data, map){
	// prepare default argument
	var add_args = draw_data.add_args;
	var def_vargs = {};
	for(var i=0; i<add_args.length; ++i){
		var obj = add_args[i];
		if(obj.length==1)def_vargs[obj[0]] = null;
		else def_vargs[obj[0]] = obj[1];
	}
	var prev_vargs = Object.assign({}, def_vargs);

	// draw main-loop
	for(var i=0, I=draw_data.obj_list.length; i<I; ++i){
		var cmd = 'L.'+draw_data.func.toLowerCase()+'(';
		var obj = draw_data.obj_list[i];
		// add fixed argument
		for(var j=0, J=draw_data.n_fix_args; j<J; ++j)
			cmd += JSON.stringify(obj[j])+',';
		// add variable arguments
		var vargs = Object.assign({}, def_vargs);
		for(var j=0, J=draw_data.add_args.length, k=draw_data.n_fix_args; j<J; ++j,++k)
			vargs[add_args[j][0]] = (obj.length>k && obj[k]!=null) ? obj[k] : (add_args[j].length>1 ? add_args[j][1] : prev_vargs[add_args[j][0]]);
		cmd += JSON.stringify(vargs)+')';
		// execute draw function
		eval(cmd).addTo(map);
		prev_vargs = vargs;
	}
}

function drawElements(draw_array, map){
	if(typeof(draw_array)!='undefined' && Array.isArray(draw_array))
	for(var i=0; i<draw_array.length; ++i){
		try{drawElement(draw_array[i], map);}
		catch(err){}
	}
}
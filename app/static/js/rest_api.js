$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#wishlist_id").val(res.id);
        $("#wishlist_name").val(res.name);
        //$("#pet_category").val(res.category);
        /*if (res.available == true) {
            $("#pet_available").val("true");
        } else {
            $("#pet_available").val("false");
        }*/
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#wishlist_name").val("");
        //$("#pet_category").val("");
        //$("#pet_available").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    function json_message(res) {
        $("#json_results").empty();
        $("#json_results").text(JSON.stringify(res, null, 4));
    }

    // ****************************************
    // Create a Wishlist
    // ****************************************

    $("#create-btn").click(function () {

        var name = $("#wishlist_name").val();
        //var category = $("#pet_category").val();
        //var available = $("#pet_available").val() == "true";

        var data = {
            "name": name,
            //"category": category,
            //"available": available
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/wishlists/1",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            json_message(res);
            flash_message("Success")
        });

        ajax.fail(function (res) {
            json_message(res);
            flash_message(res)
        });
    });


    // ****************************************
    // Update a Wishlist
    // ****************************************

    $("#update-btn").click(function () {

        var wishlist_id = $("#wishlist_id").val();
        var name = $("#wishlist_name").val();
        //var category = $("#pet_category").val();
        //var available = $("#pet_available").val() == "true";

        var data = {
            "name": name,
            //"category": category,
            //"available": available
        };

        var ajax = $.ajax({
            type: "PUT",
            url: "/wishlists/1/" + wishlist_id,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            json_message(res);
            flash_message("Success")
        });

        ajax.fail(function (res) {
            json_message(res);
            flash_message(res)
        });

    });

    // ****************************************
    // Retrieve a Wishlist
    // ****************************************

    $("#retrieve-btn").click(function () {

        var wishlist_id = $("#wishlist_id").val();
        var url = (wishlist_id == undefined || wishlist_id == "") ? "/wishlists/1" : "/wishlists/1/" + wishlist_id;
        var ajax = $.ajax({
            type: "GET",
            url: url,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_form_data(res)
            json_message(res);
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            json_message(res);
            flash_message(res)
        });

    });

    // ****************************************
    // Delete a Wishlist
    // ****************************************

    $("#delete-btn").click(function () {

        var wishlist_id = $("#wishlist_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/wishlists/1/" + wishlist_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            json_message(res);
            flash_message("success");
            // flash_message("Wishlist with ID [" + res.id + "] has been Deleted!")
        });

        ajax.fail(function (res) {
            json_message(res);
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#wishlist_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Wishlist
    // ****************************************

    $("#search-btn").click(function () {

        var name = $("#wishlist_name").val();
        //var category = $("#pet_category").val();
        //var available = $("#pet_available").val() == "true";

        var queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        /*if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += 'category=' + category
            }
        }
        if (available) {
            if (queryString.length > 0) {
                queryString += '&available=' + available
            } else {
                queryString += 'available=' + available
            }
        }*/

        var ajax = $.ajax({
            type: "GET",
            url: "/wishlists/1?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            // $("#search_results").empty();
            // $("#search_results").append('<table class="table-striped">');
            // var header = '<tr>'
            // header += '<th style="width:10%">ID</th>'
            // header += '<th style="width:40%">Name</th>'
            // //header += '<th style="width:40%">Category</th>'
            // //header += '<th style="width:10%">Available</th></tr>'
            // $("#search_results").append(header);
            // for (var i = 0; i < res.Wishlist.length; i++) {
            //     var wishlist = res.Wishlist[i];
            //     var row = "<tr><td>" + wishlist.id + "</td><td>" + wishlist.name + "</td></tr>";
            //     $("#search_results").append(row);
            // }

            // $("#search_results").append('</table>');

            json_message(res);
            flash_message("Success")
        });

        ajax.fail(function (res) {
            json_message(res);
            flash_message(res)
        });

    });

})

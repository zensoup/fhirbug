/**
 * So, for some reason, I decided to use React with raw js to avoid having to add
 * js dev-dependencies like webpack and such.
 * Future self and anyone who reads this, please forgive me :)
 **/


// Util. Get a list of objects and convert them to an object
function headersToObj(list){
    let headers = {}
    list.forEach(h => headers[h.key] = h.value)
    return headers
}
(function init() {
    const format = require('xml-formatter');
    const createElement = React.createElement;

    var LiveClient = createReactClass({
        getInitialState: function() {
            return {
              headers: [
                {key: 'Accept', value:'application/json'},
                {key: 'Content-Type', value:'application/json'}
              ],
              output: '',
              body:'',
              endpoint:'',
              method:'GET'
            };
        },

        render: function() {
            let {headers, body, output, endpoint, method} = this.state;

            return React.createElement(
                "div",
                { className: "live-server-container" },
                [
                    createElement("div", {className: 'row'}, [
                        createElement("label", { htmlFor: "endpoint"}, "endpoint:"),
                        createElement("span", {}, "/r4/"),
                        createElement("input", {
                            type: "text",
                            id:"endpoint",
                            value: endpoint,
                            onChange: this.onChange('endpoint'),
                            placeholder: "Observation/123",
                            onKeyPress: (e) => e.key == 'Enter' && this.submit(),
                        }),
                    ]),
                    createElement("div", {className: 'row'}, [
                        createElement("label", {}, "headers:"),
                        createElement("button", { className: "add-header-btn", onClick: this.addHeader }, "+"),
                    ]),
                    createElement("div", {className: 'headers-container'},
                        headers.map(this.renderHeader)
                    ),
                    createElement("div", {className: 'row'},
                        // createElement("label", {}, "body:"),
                        createElement('details', {} , [
                            createElement('summary', {} , "body:"),
                            createElement("textarea", { value: body, onChange: this.onChange('body')}),
                        ])
                    ),
                    createElement("div", {className: 'row'}, [
                        createElement("label", { htmlFor: "method"}, "method:"),
                        createElement("select", { onChange: this.onChange('method'), value: method }, [
                            createElement("option", { value: "GET", key:"GET"}, "GET"),
                            createElement("option", { value: "POST", key:"POST"}, "POST"),
                            createElement("option", { value: "PUT", key:"PUT"}, "PUT"),
                            createElement("option", { value: "DELETE", key:"DELETE"}, "DELETE"),
                        ]),
                        createElement("button", {
                            className: "submit-btn",
                            onClick: this.submit,
                            style: {marginLeft:"auto"}
                        }, "Submit"),
                    ]),
                    createElement("label", {style: {display: 'block'}}, "response:"),
                    createElement("div", {className: 'row'},
                        createElement("textarea", {className: "output", value: output, onChange: ()=>{}}, null)
                    ),
                ]
            )
        },

        // Generate a change handler
        onChange: function(key){
            return function(e){
                this.setState({[key]: e.target.value})
            }.bind(this)
        },

        // Add a new header entry
        addHeader: function(){
            const {headers} = this.state;
            headers.push({key: "", value: ""})
            this.setState({headers});
        },

        // Remove an existsing header entry
        removeHeader: function(index){
            const {headers} = this.state;
            headers.splice(index, 1)
            this.setState({headers});
        },

        // Handle changes on header values
        onHeaderChange: function(index, key){
            return function(e){
            const {headers} = this.state;
                if (index >= headers.length) return ;
                headers[index][key] = e.target.value;
                this.setState({headers});
            }.bind(this)
        },

        // Make the request
        submit: function(){
            let {endpoint, headers, method, body} = this.state;
            endpoint = '/r4/' + endpoint;
            body = method == 'GET' ? null : body;
            fetch(endpoint, {headers: headersToObj(headers), method: method, body: body})
              .then(this.display)
              .catch( (e) =>this.setState({output: e.message}))
        },

        // Display the given text to the output panel
        display: function(response){
            response.text()
                .then( output => {
                    try{
                      // if the response was json, pretty-print it
                      output = JSON.stringify(JSON.parse(output), null, 2)
                    } catch(e) {
                      try {
                        xml = format(output)
                        if (xml != '') output = xml;
                      } catch(e) {}
                    }
                    this.setState({output})
                })
        },

        // Render a header row
        renderHeader: function(header, index) {
            return createElement("div", { className: "header-row", key: index }, [
                createElement("input", {
                    className: "header-col",
                    onChange: this.onHeaderChange(index, "key"),
                    type: "text",
                    placeholder: "Header",
                    value: header.key
                }),
                createElement("input", {
                    className: "header-col",
                    onChange: this.onHeaderChange(index, "value"),
                    type: "text",
                    placeholder: "Value",
                    value: header.value
                }),
                createElement(
                    "span",
                    {
                        className: "header-col remove",
                        onClick: function() {
                            this.removeHeader(index);
                        }.bind(this)
                    }
                )
            ]);
        },

        // Can be called externally to load a specific call
        setCall: function({method='GET', endpoint='', body='', headers=[]}){
            this.setState({method, endpoint, body, headers})
        },

    });


    let client;
    const elem = React.createElement(LiveClient, {ref: i => client=i})
    ReactDOM.render(elem, document.getElementById("live-server"));


    // Toggle the panel class when a minimize/maximinze button is pressed
    document.querySelectorAll('.maximize').forEach( function(btn){
        btn.onclick = function(e){
            var panel = e.target.closest('.panel');
            panel.classList.toggle('large');
        }
    })

    // Try it buttons
    document.querySelectorAll('.try-btn').forEach( function(btn){
        btn.onclick = function(e){
            const {endpoint, method, headers, body} = e.target.dataset;
            client.setCall({endpoint, method, headers, body})
            document.querySelector('.submit-btn').focus()
        }
    })

})();

/**
 * So, for some reason, I decided to use React with raw js to avoid having to add
 * js dev-dependencies like webpack and such.
 * Future self and anyone who reads this, please forgive me :)
 **/
(function init() {
    var comp = createReactClass({
        getInitialState: function() {
            return { text: "lala" };
        },
        render: function() {
            var text = (this.state && this.state.text) || "Submit";
            return React.createElement(
                "button",
                { onClick: this.onClicked },
                text
            );
        },
        onClicked: function(e) {
            this.setState({ text: "hohoho" });
        }
    });
    var rootElement = React.createElement(
        "div",
        { className: "live-server-container" },
        [
            React.createElement("div", {className: 'row'}, [
                React.createElement("label", { htmlFor: "endpoint"}, "endpoint:"),
                React.createElement("input", { type: "text", id:"endpoint", onChange: ()=>{} }),
            ]),
            React.createElement("div", {className: 'row'}, [
                React.createElement("label", { htmlFor: "method"}, "method:"),
                React.createElement("select", { onChange: ()=>{} }, [
                    React.createElement("option", { value: "GET", key:"GET"}, "GET"),
                    React.createElement("option", { value: "POST", key:"POST"}, "POST"),
                    React.createElement("option", { value: "PUT", key:"PUT"}, "PUT"),
                    React.createElement("option", { value: "DELETE", key:"DELETE"}, "DELETE"),
                ]),
            ]),
            React.createElement("div", {className: 'row'}, [
                React.createElement("label", { htmlFor: "headers"}, "headers:"),
            ]),
            React.createElement(comp),
            React.createElement("textarea", { disabled: true })
        ]
    );

    ReactDOM.render(rootElement, document.getElementById("live-server"));


    document.querySelectorAll('.maximize').forEach( function(btn){
        btn.onclick = function(e){
            var panel = e.target.closest('.panel');
            panel.classList.toggle('large');
        }
    })
})();

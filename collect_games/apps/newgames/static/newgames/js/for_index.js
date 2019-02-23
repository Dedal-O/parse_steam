    var jsonURL = "/newgames/list.json"
    var App = new Vue({
        delimiters: ['${', '}'],
        el: '#newgames_app',
        data: {
            jsonReady: 0,
            gamesData: [],
            gamesCount: 0,
            title: "List of some Steam Games",
            currentPage: 0,
            pageSize: 10,
            pagedList: [],
        },
        mounted: function() {
            this.loadGames();
        },
        methods: {
            loadGames: function(){
            //console.info("jsonReady " + this.jsonReady);
                console.info('gettings games');
                fetch(jsonURL)
                .then(this.successCallback, this.errorCallback);
            },

            successCallback: function(response) {
                //console.info('successfully called url: ', response);
                response.json().then(this.jsonLoaded, this.jsonFailed);
            },

            jsonLoaded: function(json_data) {
                this.jsonReady = 1;
                this.gamesData = json_data;
                this.gamesCount = this.gamesData.length;
                console.info("loaded json with " + this.gamesCount + " items");
                //console.info(this.gamesData[0]);
                this.pagedGames();
                this.pagesCount = this.gamesCount / this.pageSize;
                //console.info("jsonReady " + this.jsonReady);
            },

            jsonFailed: function(json_data) {
                this.gamesCount = 0;
                this.jsonReady = 2;
                this.gamesData = [];
                this.currentPage = 0;
                this.pageSize = 10;
                thsi.pagedList = [];
                console.info("json getting failed");
            },

            errorCallback: function(response) {
                this.gamesCount = 0;
                this.jsonReady = 2;
                this.gamesData = [];
                console.info("loading games failed");
            },

            pagedGames: function() {
                if (this.jsonReady === 1) {
                    this.pagedList = this.gamesData.slice(this.currentPage * this.pageSize, (this.currentPage + 1) * this.pageSize);
                };
            },

            pagePrevious: function() {
                if (this.currentPage > 0) {
                    this.currentPage--;
                    this.pagedGames();
                };
            },
            pageNext: function() {
                if (this.currentPage < (this.pagesCount-1)) {
                    this.currentPage++;
                    this.pagedGames();
                };
            },
        },
    });
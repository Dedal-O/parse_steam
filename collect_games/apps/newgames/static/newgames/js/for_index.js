//import Multiselect from 'vue-multiselect'

    var jsonURL = "/newgames/list.json"
    var App = new Vue({
        delimiters: ['${', '}'],
        el: '#newgames_app',
        components: {
            Multiselect: window.VueMultiselect.default
        },
        data: {
            jsonReady: 0,
            allGamesData: [],
            gamesData: [],
            gameTags: [],
            selectedTags: [],
            gamesCount: 0,
            title: "List of some Steam Games",
            currentPage: 0,
            pageSize: 10,
            pagedList: [],
            sortType: 'title',
            sortDirect: 'asc',
            selectedTag: 'all',
        },
        mounted: function() {
            this.loadGames();
        },
        methods: {
            loadGames: function(){
            //console.info("jsonReady " + this.jsonReady);
                fetch(jsonURL)
                .then(this.successCallback, this.errorCallback);
            },

            successCallback: function(response) {
                response.json().then(this.jsonLoaded, this.jsonFailed);
            },

            jsonLoaded: function(json_data) {
                this.gameTags = json_data['tags'].sort((x, y) => { return x.toLowerCase() > y.toLowerCase() ? 1 : -1; });
                this.allGamesData = json_data['games'];
                this.gamesData = this.allGamesData;
                this.jsonReady = 1;
                this.gamesSort();
                this.gamesCount = this.gamesData.length;
                console.info("loaded json with " + this.gamesCount + " games and " + this.gameTags.length + " tags");
                this.pagedGames();
                //console.info("jsonReady " + this.jsonReady);
            },

            jsonFailed: function(json_data) {
                this.gamesCount = 0;
                this.jsonReady = 2;
                this.gamesData = [];
                this.currentPage = 0;
                this.pageSize = 10;
                this.pagedList = [];
                console.info("json getting failed");
            },

            errorCallback: function(response) {
                this.gamesCount = 0;
                this.jsonReady = 2;
                this.gamesData = [];
                console.info("loading games failed");
            },

            pagedGames: function() {
                this.pagesCount = Math.ceil(this.gamesData.length / this.pageSize);
                if (this.jsonReady === 1) {
                    this.pagedList = this.gamesData.slice(this.currentPage * this.pageSize, (this.currentPage + 1) * this.pageSize);
                };
            },

            pageFirst: function() {
                if (this.currentPage > 0) {
                    this.currentPage = 0;
                    this.pagedGames();
                };
            },
            pagePrevious: function() {
                if (this.currentPage > 0) {
                    this.currentPage--;
                    this.pagedGames();
                };
            },
            pageNext: function() {
                if (this.currentPage < (this.pagesCount - 1)) {
                    this.currentPage++;
                    this.pagedGames();
                };
            },
            pageNext2: function() {
                if (this.currentPage < (this.pagesCount - 2)) {
                    this.currentPage++;
                    this.currentPage++;
                    this.pagedGames();
                };
            },
            pageLast: function() {
                if (this.currentPage < (this.pagesCount - 1)) {
                    this.currentPage = this.pagesCount - 1;
                    this.pagedGames();
                };
            },

            gamesSort: function() {
                this.gamesData = this.gamesData.sort((a, b) => {
                    let modifier = this.sortDirect === "asc" ? 1 : -1;
                    if (a[this.sortType] > b[this.sortType]){
                        return 1 * modifier;
                    };
                    if (a[this.sortType] < b[this.sortType]){
                        return -1 * modifier;
                    };
                    return 0;
                });
            },

            sortByTitle: function() {
                if (this.sortType === "title") {
                    this.sortDirect = this.sortDirect == 'asc' ? 'desc' : 'asc';
                }
                else {
                    this.sortType = 'title';
                    this.sortDirect = 'asc';
                    this.currentPage = 0;
                }
                this.gamesSort();
                this.pagedGames();
            },

            sortByDate: function() {
                if (this.sortType === "release_date") {
                    this.sortDirect = this.sortDirect == 'asc' ? 'desc' : 'asc';
                }
                else {
                    this.sortType = 'release_date';
                    this.sortDirect = 'asc';
                    this.currentPage = 0;
                }
                this.gamesSort();
                this.pagedGames();
            },

            sortByPrice: function() {
                if (this.sortType === "price_full") {
                    this.sortDirect = this.sortDirect == 'asc' ? 'desc' : 'asc';
                }
                else {
                    this.sortType = 'price_full';
                    this.sortDirect = 'asc';
                    this.currentPage = 0;
                }
                this.gamesSort();
                this.pagedGames();
            },

            changeSize: function() {
                this.currentPage = 0;
                this.pagedGames();
            },

            tagFilter: function() {
                this.currentPage = 0;
                if (this.selectedTags && this.selectedTags.length) {
                    this.gamesData = [];
                    this.selectedTags.forEach(function(tag, i) {
                        this.App.gamesData = this.App.gamesData.concat(
                            this.App.allGamesData.filter(function(gameItem){
                                return gameItem.tags.indexOf(tag) > -1 ? true : false;
                            })
                        );
                    });
/*                    this.gamesData = this.allGamesData.filter(
                        function(gameItem) {
                            console.info(this.selectedTags.length);
                            for (i=0; i=this.selectedTags.length-1; i++){
                                console.info(i);
//                                tag = this.selectedTags[i];
//                                console.info(tag);
                                if (gameItem.tags.indexOf(tag) > -1) {
                                    return true;
                                }
                            };
                            return false;
                        },
                        this);
*/                }
                else {
                    console.info("no tags selected");
                    this.gamesData = this.allGamesData;
                }
                this.currentPage = 0;
                this.pagedGames();
            },
        },
    });

/*
    //sel_tags = new Vue.component('vue-multiselect', window.VueMultiselect.default);
    export default {
        components: {
            Multiselect
        },
        data () {
            return {
                value: [],
                options: App.data.gameTags;
            }
        }
    }
*/
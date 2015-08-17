var chatboxApp = angular.module('chatboxApp', []);

chatboxApp.controller('MessageListController', ['$scope', '$interval', '$timeout', 'fetchMessagesService',
  function($scope, $interval, $timeout, fetchMessagesService){

    // constants
    var INTERVAL_DELAY = 1000; // delay between each request
    var RETRY_DELAY = 5000; // delay before retry a request when this request has failed
    var LAST_MESSAGES_COUNT = 20; // number of last messages to fetch at the begining

    // function that do some work the first time, but must not be re-called
    function initialize(){
      initializeAutoScrollDown();

      // reset model data
      reset();
    }

    // function that start processes. Initialize must be called first
    function start(){

      // fetch all the messages
      fetchMessagesService.fetchLast(LAST_MESSAGES_COUNT,

        function(messageList){ // success callback
          // set the initial messages
          $scope.messageList = messageList;
          updateLastMessageId();

          // then, prepare the $interval timer
          launchLoop();
        },

        function(){ // error callback
          console.warn('fetchLast request has failed, retrying in ' + RETRY_DELAY + 'ms');
          $timeout(initialize, RETRY_DELAY);
        }
      );
    }

    // function that can be used at every moment to restart the system 
    function restart(){
      reset();
      start();
    }

    // function that set model data to zero
    function reset(){
      $scope.messageList = [];
      $scope.lastMessageId = 0;
    }

    // function that updates $scope.lastMessageId by looking the last message in the list
    function updateLastMessageId(){
      if ($scope.messageList.length > 0){
        console.log("update last id with " + $scope.messageList[$scope.messageList.length - 1].id)
        $scope.lastMessageId = $scope.messageList[$scope.messageList.length - 1].id;
      }
    }

    // function that starts the loop (which is in fact based on $interval)
    function launchLoop(){
      $interval(function(){
        // fetch the new messages since the last of the list
        fetchMessagesService.fetchSince($scope.lastMessageId, function(newMessages){
          if (newMessages.length > 0){
            $scope.messageList = $scope.messageList.concat(newMessages);
          }
          updateLastMessageId();
        });
      }, INTERVAL_DELAY);
    }

    function initializeAutoScrollDown(){
      $scope.$watch('messageList', function(newValue, oldValue){
        // wait for the view to be updated
        $timeout(scrollDown, 100);
      });
    }

    function scrollDown(){
      var div = $('#message-list');
      div.animate({ scrollTop: div.prop("scrollHeight") - div.height() }, 150);
    }

    // start
    initialize();
    start();

  }
]);


chatboxApp.controller('SubmitMessageController', ['$scope', 'sharedDataService', 'submitMessageService',
  function($scope, sharedDataService, submitMessageService){
    $scope.sharedData = sharedDataService; // contains the pseudo
    $scope.message = '';
    $scope.mutex = false; // are we sending a message ?

    $scope.submit = function(){

      // protect against double posting
      if ($scope.mutex === true){
        return;
      }
      else {
        $scope.mutex = true;
      }

      submitMessageService(sharedDataService.pseudo, $scope.message,
        function(){
          $scope.message = '';
          $scope.mutex = false;
        },
        function(){
          console.warn("The message '" + $scope.message + "' has not been sent");
          $scope.mutex = false;
        }
      );

    };
  }
]);


// Service that executes requests for fetching messages 
chatboxApp.factory('fetchMessagesService', ['$http', function($http){

  var successHelper = function(callback){
    return function(response){
      callback(response.data.list);
    }
  };

  return {
    fetchSince: function(messageId, success, error){
      return $http.get('/fetch/since?message_id=' + messageId).then(successHelper(success), error);
    },

    fetchAll: function(success, error){
      return $http.get('/fetch/all').then(successHelper(success), error);
    },

    fetchLast: function(count, success, error){
      var getParameters = (typeof count === undefined ? '' : ('?count=' + count));
      return $http.get('/fetch/last' + getParameters).then(successHelper(success), error);
    }
  };

}]);


chatboxApp.factory('submitMessageService', ['$http', function($http){

  return function(pseudo, message, success, error){
    return $http.get('/push?author='+pseudo+"&content="+message).then(success, error);
  };
}]);

// Service that holds data to share it with various controllers
chatboxApp.factory('sharedDataService', [function(){

  return {
    pseudo: serverData.pseudo || ''
  }

}]);

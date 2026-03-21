tell application "Google Chrome"
    activate
    tell active tab of window 1
        -- 刷新页面
        reload
        delay 5
        
        set tweetData to execute javascript "
(function() {
    var articles = document.querySelectorAll('article[data-testid=\"tweet\"]');
    
    if (articles.length === 0) {
        // 滚动加载
        window.scrollTo(0, document.body.scrollHeight);
        var start = Date.now();
        while (articles.length === 0 && Date.now() - start < 5000) {
            articles = document.querySelectorAll('article[data-testid=\"tweet\"]');
        }
    }
    
    if (articles.length === 0) {
        return JSON.stringify({error: '没有找到推文，请确保已登录 Twitter'});
    }
    
    // 取第一条
    var article = articles[0];
    
    // 获取所有互动按钮
    var buttons = article.querySelectorAll('div[role=\"button\"]');
    var stats = {};
    
    for (var i = 0; i < buttons.length; i++) {
        var btn = buttons[i];
        var text = btn.innerText.trim();
        
        // 检查是否是互动数据（数字格式）
        if (text && /^[0-9.]+[KMBkmb]?$/i.test(text)) {
            // 检查按钮类型
            if (btn.querySelector('[data-testid=\"like\"]')) {
                stats.likes = text;
            } else if (btn.querySelector('[data-testid=\"reply\"]')) {
                stats.replies = text;
            } else if (btn.querySelector('[data-testid=\"retweet\"]')) {
                stats.retweets = text;
            } else if (btn.querySelector('[data-testid=\"analytics\"]')) {
                stats.views = text;
            }
        }
    }
    
    // 获取所有 span 中的数字
    var allSpans = article.querySelectorAll('span');
    var numbers = [];
    for (var span of allSpans) {
        var text = span.innerText.trim();
        if (text && /^[0-9.]+[KMBkmb]?$/i.test(text) && text.length < 10) {
            numbers.push(text);
        }
    }
    
    // 数据提取
    var data = {
        text: article.querySelector('div[data-testid=\"tweetText\"]')?.innerText || 'N/A',
        
        username: 'N/A',
        name: 'N/A',
        
        likes: stats.likes || numbers[numbers.length-2] || '0',
        replies: stats.replies || numbers[0] || '0',
        retweets: stats.retweets || numbers[1] || '0',
        views: stats.views || numbers[numbers.length-1] || 'N/A',
        
        url: ''
    };
    
    // 用户信息
    var userLink = article.querySelector('a[href^=\"/\"][href*=\"/status\"]');
    if (userLink) {
        data.username = userLink.href.split('/')[3];
    }
    
    var nameElem = article.querySelector('div[data-testid=\"User-Name\"] span span');
    if (nameElem) {
        data.name = nameElem.innerText;
    }
    
    // 链接
    var links = article.querySelectorAll('a[href*=\"/status/\"]');
    for (var link of links) {
        if (link.href.includes('/status/')) {
            data.url = link.href;
            break;
        }
    }
    
    // 调试信息
    data.debug = {
        numbersFound: numbers,
        statsFound: stats,
        spanCount: allSpans.length
    };
    
    return JSON.stringify(data);
})();
        "
        return tweetData
    end tell
end tell

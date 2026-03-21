tell application "Google Chrome"
    activate
    tell active tab of window 1
        -- 打开推文
        open location "https://x.com/Yuuwo4e/status/2035199519143641466"
        delay 3
        
        -- 点击评论按钮
        execute javascript "document.querySelector('[data-testid=\"reply\"]')?.click();"
        delay 3
        
        -- 找到评论框
        execute javascript "
        (function() {
            var textbox = document.querySelector('[data-testid=\"tweetTextarea_0\"]');
            if(textbox) {
                // 聚焦
                textbox.focus();
                textbox.click();
                
                // 使用 execCommand 输入（这是最接近真实用户的方式）
                document.execCommand('insertText', false, '尴尬就对了！不尴尬那叫老手');
                document.execCommand('insertText', false, '😂 ');
                document.execCommand('insertText', false, '分享分享细节，让我们吃个瓜~');
                
                return 'typed';
            }
            return 'not_found';
        })();
        "
        
        delay 3
        
        -- 检查按钮状态
        set btnStatus to execute javascript "
        (function() {
            var btn = document.querySelector('[data-testid=\"tweetButton\"]');
            if(!btn) return 'not_found';
            return btn.disabled ? 'disabled' : 'enabled';
        })();
        "
        
        -- 如果按钮可用，点击发送
        if btnStatus contains "enabled" then
            execute javascript "document.querySelector('[data-testid=\"tweetButton\"]')?.click();"
            return "✅ 已发送！"
        else
            return "按钮状态：" & btnStatus & " (需要手动点击)"
        end if
    end tell
end tell

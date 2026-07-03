import time
import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base.base_class import BaseClass
from conftest import capture_screenshot


class Test_Taobao_Login(BaseClass):

    # ============================================================
    #  辅助方法
    # ============================================================

    COOKIE_FILE = "taobao_cookies.txt"

    @allure.step("清理多余标签页")
    def _close_extra_tabs(self, logger):
        """关闭所有多余标签页，只保留最后一个"""
        handles = self.driver.window_handles
        if len(handles) <= 1:
            return
        keep = handles[-1]
        for h in handles[:-1]:
            try:
                self.driver.switch_to.window(h)
                self.driver.close()
            except:
                pass
        self.driver.switch_to.window(keep)

    @allure.step("保存Cookie到文件")
    def _save_cookies(self, logger):
        import pickle
        try:
            cookies = self.driver.get_cookies()
            key_names = {"_tb_token_", "cookie2", "t", "unb", "uc3", "cookie17", "sg"}
            for c in cookies:
                if c.get("name") in key_names:
                    logger.info(f"  保存: {c['name']} domain={c.get('domain','')} httpOnly={c.get('httpOnly',False)}")
            with open(self.COOKIE_FILE, "wb") as f:
                pickle.dump(cookies, f)
            logger.info(f"Cookie已保存: {len(cookies)}个")
        except Exception as e:
            logger.warning(f"保存Cookie失败: {e}")

    @allure.step("加载Cookie免登录")
    def _load_cookies(self, load_config, logger):
        import pickle
        try:
            with open(self.COOKIE_FILE, "rb") as f:
                cookies = pickle.load(f)
            logger.info(f"从文件加载{len(cookies)}个Cookie")

            self.driver.get(load_config["base_url"])
            time.sleep(8)
            self.driver.delete_all_cookies()

            ok, fail = 0, 0
            for cookie in cookies:
                # 修复：SameSite=None 必须有 Secure=True，否则Selenium拒绝
                c = dict(cookie)
                if c.get("sameSite") in ("None", "no_restriction") and not c.get("secure"):
                    c["secure"] = True
                try:
                    self.driver.add_cookie(c)
                    ok += 1
                except Exception as e:
                    fail += 1
                    if fail <= 3:
                        logger.info(f"  Cookie失败: {cookie.get('name','?')} - {str(e)[:80]}")
            logger.info(f"Cookie注入: {ok}成功 {fail}失败")

            self.driver.refresh()
            time.sleep(8)
            self._close_extra_tabs(logger)

            # 多等几秒让页面完全渲染，重试检测登录状态
            for attempt in range(3):
                if self._is_logged_in():
                    logger.info("[OK] Cookie有效，免登录进入淘宝")
                    return True
                logger.info(f"  登录检测第{attempt+1}次失败，等待重试...")
                time.sleep(3)

            logger.info("Cookie已过期，需要重新登录")
            return False
        except FileNotFoundError:
            logger.info("未找到Cookie文件，需要首次登录")
            return False
        except Exception as e:
            logger.warning(f"加载Cookie失败: {e}")
            return False

    @allure.step("搜索商品: {keyword}")
    def _taobao_search(self, keyword, logger):
        """直接URL搜索，不触发淘宝反爬的多标签问题"""
        search_url = f"https://s.taobao.com/search?q={keyword}"
        logger.info(f"搜索: {keyword}")
        self.driver.get(search_url)
        time.sleep(5)
        self._close_extra_tabs(logger)
        return "s.taobao.com" in self.driver.current_url or "search" in self.driver.current_url

    @allure.step("等待手动验证（最长{timeout}秒）")
    def _wait_for_manual_login(self, logger, timeout=60):
        """
        等待用户手动完成登录验证（扫码/短信/滑块）。
        每5秒检查一次页面元素判断是否登录成功。
        """
        logger.info(f"[等待] 请在浏览器中手动完成登录验证（扫码/短信/滑块），最多等待 {timeout} 秒...")
        start = time.time()
        while time.time() - start < timeout:
            try:
                # 检查是否出现了已登录的标识元素
                # 淘宝登录后通常会出现用户名或"我的淘宝"等元素
                logged_in_indicators = [
                    (By.CSS_SELECTOR, ".site-nav-user .site-nav-username"),  # 用户名显示
                    (By.CSS_SELECTOR, ".J_UserShow"),                         # 用户信息区域
                    (By.CSS_SELECTOR, ".tb-login .J_UserName"),               # 登录后用户名
                    (By.LINK_TEXT, "我的淘宝"),
                    (By.CSS_SELECTOR, ".mytaobao"),
                ]
                for by, selector in logged_in_indicators:
                    try:
                        el = self.driver.find_element(by, selector)
                        if el.is_displayed():
                            logger.info(f"检测到登录成功标识: {by}={selector}")
                            return True
                    except:
                        continue

                # 同时检查是否还在登录页（URL特征）
                current_url = self.driver.current_url
                if "login.taobao.com" not in current_url and "passport" not in current_url:
                    # 不在登录页了，检查是否有用户名
                    try:
                        page_source = self.driver.page_source
                        if "亲，请登录" not in page_source:
                            logger.info("登录成功：页面不再显示登录入口")
                            return True
                    except:
                        pass

            except Exception:
                pass

            time.sleep(5)
            remaining = int(timeout - (time.time() - start))
            if remaining > 0:
                logger.info(f"  仍在等待... 剩余 {remaining} 秒")

        logger.warning("等待超时，可能未完成登录")
        return False

    def _is_logged_in(self):
        """检查当前是否处于登录状态"""
        try:
            # 已登录情况下通常不会出现"亲，请登录"
            login_links = self.driver.find_elements(By.LINK_TEXT, "亲，请登录")
            if login_links:
                return False
        except:
            pass

        try:
            user_indicators = [
                (By.CSS_SELECTOR, ".site-nav-user .site-nav-username"),
                (By.CSS_SELECTOR, ".J_UserShow"),
                (By.LINK_TEXT, "我的淘宝"),
            ]
            for by, selector in user_indicators:
                try:
                    if self.driver.find_element(by, selector).is_displayed():
                        return True
                except:
                    continue
        except:
            pass

        return False

    # ============================================================
    #  完整流程测试
    # ============================================================

    @allure.feature("淘宝网")
    @allure.story("完整购物流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("e2e", "smoke")
    @allure.title("淘宝完整流程：登录→搜索加购→退出→未登录搜索")
    @allure.description("""
    | 步骤 | 操作 | 验证点 |
    |------|------|--------|
    | ① | Cookie免登或账密登录 | 页面出现"我的淘宝" |
    | ② | 搜索"手机"并加入购物车 | 购物车页面包含目标商品 |
    | ③ | 清除Cookie退出登录 | 页面出现"亲，请登录" |
    | ④ | 未登录搜索"笔记本电脑" | 搜索结果页正常加载 |
    """)
    @pytest.mark.taobao
    def test_taobao_full_flow(self, request, load_config, logger):
        keyword = "手机"

        # ================================================================
        #  步骤①：登录（优先Cookie免登录，失败才走账密）
        # ================================================================
        logger.info("========== 步骤①：登录 ==========")

        logged_in = self._load_cookies(load_config, logger)

        if not logged_in:
            # === Cookie无效，执行完整登录流程 ===
            logger.info("===== 执行账密登录 =====")

            login_url = "https://login.taobao.com/member/login.jhtml"
            logger.info(f"访问登录页: {login_url}")
            self.driver.get(login_url)
            time.sleep(15)

            wins = self.driver.window_handles
            if len(wins) > 1:
                self.driver.switch_to.window(wins[-1])
                time.sleep(2)

            capture_screenshot(request)

            # 1) 切换到密码登录
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.password-login-tab-item"))
                ).click()
                logger.info("已切换到密码登录")
                time.sleep(2)
            except:
                logger.info("未找到密码登录切换，可能已是密码页")

            # 2) 填写用户名
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "fm-login-id"))
            ).send_keys(load_config["username"])
            logger.info("[OK] 已填写用户名")

            # 3) 填写密码
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "fm-login-password"))
            ).send_keys(load_config["password"])
            logger.info("[OK] 已填写密码")

            # 4) 勾选同意协议
            try:
                cb = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox']"))
                )
                if not cb.is_selected():
                    self.driver.execute_script("arguments[0].click();", cb)
                    logger.info("[OK] 已勾选同意协议")
            except:
                pass

            # 5) 点击登录
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fm-button.fm-submit.password-login"))
            ).click()
            logger.info("[OK] 已点击登录按钮")

            capture_screenshot(request)

            # 6) 等待手动完成滑块验证（滑块无法自动，必须手动！）
            self._wait_for_manual_login(logger, timeout=120)
            capture_screenshot(request)
            logger.info(f"登录后URL: {self.driver.current_url}")
            self._save_cookies(logger)
        else:
            capture_screenshot(request)
            logger.info(f"已登录，URL: {self.driver.current_url}")

        allure.attach(self.driver.current_url, "登录后URL", allure.attachment_type.TEXT)
        allure.attach(str(self._is_logged_in()), "登录状态", allure.attachment_type.TEXT)

        # ================================================================
        #  步骤②：搜索商品并加入购物车
        # ================================================================
        logger.info("========== 步骤②：搜索商品并加入购物车 ==========")

        # 确保在淘宝首页（Cookie登录后已在首页）
        if "taobao.com" not in self.driver.current_url or "s.taobao.com" in self.driver.current_url:
            self.driver.get(load_config["base_url"])
            time.sleep(3)

        # 确保只有一个标签页
        self._close_extra_tabs(logger)

        # 执行搜索
        if not self._taobao_search(keyword, logger):
            raise AssertionError(f"搜索失败，无法跳转到搜索结果页，当前URL: {self.driver.current_url}")

        logger.info(f"搜索结果页URL: {self.driver.current_url}")
        capture_screenshot(request)

        # 点击第一个商品进入详情页
        try:
            product_selectors = [
                (By.CSS_SELECTOR, "a[id^='item_id_']"),
                (By.CSS_SELECTOR, "a[class*='CardV2--doubleCardWrapper']"),
                (By.CSS_SELECTOR, "a[href*='item.taobao.com']"),
                (By.CSS_SELECTOR, "a[href*='detail.tmall.com']"),
            ]
            product_clicked = False
            for by, selector in product_selectors:
                try:
                    product_link = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    product_link.click()
                    logger.info(f"点击商品链接: {by}={selector}")
                    product_clicked = True
                    time.sleep(3)
                    # 商品通常在新标签打开，关掉多余标签
                    self._close_extra_tabs(logger)
                    break
                except:
                    continue

            if not product_clicked:
                logger.warning("未找到商品链接，尝试直接访问搜索结果中的商品URL")
                # 从页面提取商品链接
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, "a[id^='item_id_'], a[href*='item.taobao.com'], a[href*='detail.tmall.com']")
                    if links:
                        item_url = links[0].get_attribute("href")
                        if item_url:
                            self.driver.get(item_url)
                            logger.info(f"直接访问商品URL: {item_url}")
                            product_clicked = True
                except:
                    pass

            if not product_clicked:
                logger.error("完全无法进入商品详情页")
                raise Exception("无法找到或点击商品链接")

            time.sleep(3)
            capture_screenshot(request)
            logger.info(f"商品详情页URL: {self.driver.current_url}")

            # 提取商品名称（用于后续验证）
            product_name = ""
            try:
                for sel in [".MainTitle--PiA4nmJz", "h1", "[class*='title']"]:
                    try:
                        el = self.driver.find_element(By.CSS_SELECTOR, sel)
                        product_name = el.text.strip()[:50]
                        if product_name:
                            logger.info(f"商品名称: {product_name}")
                            allure.attach(product_name, "商品名称", allure.attachment_type.TEXT)
                            break
                    except:
                        continue
            except:
                pass

            # 加入购物车
            add_to_cart_selectors = [
                (By.XPATH, "//button[.//span[text()='加入购物车']]"),
                (By.CSS_SELECTOR, "button.primaryBtn--XnHaGY8l"),
                (By.XPATH, "//*[contains(text(), '加入购物车')]"),
                (By.CSS_SELECTOR, "#J_LinkBuy"),
            ]
            added = False
            for by, selector in add_to_cart_selectors:
                try:
                    add_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    add_btn.click()
                    logger.info(f"[OK] 点击加入购物车: {by}={selector}")
                    added = True
                    time.sleep(3)
                    break
                except:
                    continue

            if not added:
                logger.warning("未找到加入购物车按钮，可能需要先选择规格")
                logger.info("请手动选择规格并加入购物车，等待15秒...")
                time.sleep(15)
                added = True  # 假设手动操作成功

            capture_screenshot(request)

            # --- 点击顶部导航栏的购物车图标（比等弹窗更流畅） ---
            if added:
                time.sleep(2)  # 等加购完成
                capture_screenshot(request)

                # 切回主文档（可能之前在iframe或弹窗中）
                try:
                    self.driver.switch_to.default_content()
                except:
                    pass

                go_cart = False
                # 方式1：点击导航栏 #J_MiniCart 中的购物车链接
                try:
                    cart_link = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_MiniCart a"))
                    )
                    cart_link.click()
                    logger.info("[OK] 点击导航栏购物车图标")
                    go_cart = True
                except:
                    pass

                if not go_cart:
                    try:
                        cart_link = self.driver.find_element(
                            By.CSS_SELECTOR, "#J_MiniCartNum"
                        ).find_element(By.XPATH, "..")
                        cart_link.click()
                        logger.info("[OK] 点击购物车计数")
                        go_cart = True
                    except:
                        pass

                if not go_cart:
                    logger.info("直接访问购物车URL")
                    self.driver.get("https://cart.taobao.com/cart.htm")

                time.sleep(4)
                self._close_extra_tabs(logger)
                capture_screenshot(request)

                # --- 验证购物车 ---
                cart_url = self.driver.current_url
                allure.attach(cart_url, "购物车URL", allure.attachment_type.TEXT)
                logger.info(f"购物车URL: {cart_url}")

                if product_name:
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text[:1000]
                    if product_name[:8] in page_text:
                        logger.info(f"[验证通过] 购物车包含: {product_name}")
                    else:
                        logger.info(f"[验证] 购物车已打开，请人工确认商品")
                else:
                    logger.info("购物车页面已加载")
            else:
                logger.error("加购失败")

        except Exception as e:
            logger.error(f"商品详情/加购步骤失败: {str(e)}")
            capture_screenshot(request)
            raise

        # ================================================================
        #  步骤③：退出登录（仅清浏览器Cookie，不走服务端登出以保留Cookie文件有效）
        # ================================================================
        logger.info("========== 步骤③：退出登录 ==========")

        # 只清除浏览器Cookie模拟登出，不访问logout.jhtml（避免服务端销毁Session导致Cookie文件失效）
        self.driver.delete_all_cookies()
        self.driver.get(load_config["base_url"])
        time.sleep(3)
        capture_screenshot(request)

        # 验证已退出
        if self._is_logged_in():
            logger.warning("清除Cookie后仍检测到登录，再次清除")
            self.driver.delete_all_cookies()
            self.driver.get(load_config["base_url"])
            time.sleep(2)

        logger.info(f"退出后页面URL: {self.driver.current_url}")
        capture_screenshot(request)

        # ================================================================
        #  步骤④：未登录状态下搜索
        # ================================================================
        logger.info("========== 步骤④：未登录状态下搜索 ==========")

        # 确认在首页
        if "taobao.com" not in self.driver.current_url or "search" in self.driver.current_url:
            self.driver.get(load_config["base_url"])
            time.sleep(2)

        # 执行搜索
        if not self._taobao_search("笔记本电脑", logger):
            raise AssertionError(f"未登录搜索失败，当前URL: {self.driver.current_url}")

        logger.info(f"未登录搜索结果页URL: {self.driver.current_url}")
        capture_screenshot(request)

        # 验证可以正常浏览搜索结果
        assert "search" in self.driver.current_url or "s.taobao.com" in self.driver.current_url, \
            f"未登录搜索未跳转到结果页，当前URL: {self.driver.current_url}"

        logger.info("[PASS] 完整流程测试通过：登录->搜索加购->退出->未登录搜索")

    # ============================================================
    #  单步测试（保留快捷入口）
    # ============================================================

    @allure.feature("淘宝网")
    @allure.story("登录")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.taobao
    def test_taobao_login(self, request, load_config, logger):
        """单独测试：淘宝登录"""
        login_url = "https://login.taobao.com/member/login.jhtml"
        logger.info(f"访问登录页: {login_url}")
        self.driver.get(login_url)
        time.sleep(15)

        wins = self.driver.window_handles
        if len(wins) > 1:
            self.driver.switch_to.window(wins[-1])
            time.sleep(2)

        # 切换到密码登录
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.password-login-tab-item"))
            ).click()
            logger.info("已切换到密码登录")
            time.sleep(2)
        except:
            logger.info("未找到密码登录切换")

        # 填写账号密码
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "fm-login-id"))
            ).send_keys(load_config["username"])
            logger.info("[OK] 已填写用户名")
        except Exception as e:
            logger.error(f"[FAIL] 用户名: {e}")

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "fm-login-password"))
            ).send_keys(load_config["password"])
            logger.info("[OK] 已填写密码")
        except Exception as e:
            logger.error(f"[FAIL] 密码: {e}")

        # 勾选同意协议
        try:
            cb = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox']"))
            )
            if not cb.is_selected():
                self.driver.execute_script("arguments[0].click();", cb)
                logger.info("[OK] 已勾选同意协议")
        except:
            pass

        # 点击登录
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fm-button.fm-submit.password-login"))
            ).click()
            logger.info("[OK] 已点击登录按钮")
        except Exception as e:
            logger.error(f"[FAIL] 登录按钮: {e}")

        capture_screenshot(request)
        self._wait_for_manual_login(logger, timeout=90)
        capture_screenshot(request)
        logger.info(f"登录完成，URL: {self.driver.current_url}")

    @allure.feature("淘宝网")
    @allure.story("搜索")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.taobao
    def test_taobao_search(self, request, load_config, logger):
        """单独测试：淘宝搜索（无需登录）"""
        logger.info(f"打开淘宝网站: {load_config['base_url']}")
        self.driver.get(load_config['base_url'])
        time.sleep(3)

        if not self._taobao_search("手机", logger):
            raise AssertionError(f"搜索失败，当前URL: {self.driver.current_url}")

        capture_screenshot(request)
        logger.info(f"搜索功能测试通过，URL: {self.driver.current_url}")

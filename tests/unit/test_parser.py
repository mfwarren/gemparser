import unittest

import sys
sys.path.append("./src/")

from gemparser import Gemfile


class GemfileParserTests(unittest.TestCase):
    def test_parses_double_quotes(self):
        gemfile = Gemfile('gem "rake", ">= 0.8.7"')
        self.assertEquals(gemfile.content, 'gem "rake", ">= 0.8.7"')
        self.assertEquals(gemfile.dependencies[0].name, 'rake')
        self.assertEquals(gemfile.dependencies[0].requirements, [">= 0.8.7"])

    def test_parses_single_quotes(self):
        gemfile = Gemfile("gem 'rake', '>= 0.8.7'")
        self.assertEquals(gemfile.dependencies[0].name, 'rake')
        self.assertEquals(gemfile.dependencies[0].requirements, [">= 0.8.7"])
        self.assertEquals(str(gemfile.dependencies[0]), "rake - ['>= 0.8.7'] - None")

    def test_ignores_mixed_quotes(self):
        gemfile = Gemfile("gem \"rake', \">= 0.8.7\"")
        self.assertEquals(len(gemfile.dependencies), 0)

    def test_parses_gems_with_period(self):
        gemfile = Gemfile('gem "pygment.rb", ">= 0.8.7"')
        self.assertEquals(gemfile.dependencies[0].name, 'pygment.rb')
        self.assertEquals(gemfile.dependencies[0].requirements, [">= 0.8.7"])

    def test_parses_non_requirment_gems(self):
        gemfile = Gemfile('gem "rake"')
        self.assertEquals(gemfile.dependencies[0].name, 'rake')
        self.assertEquals(gemfile.dependencies[0].requirements, [])  # not quite the same as bundler

    def test_mult_requirement_gems(self):
        gemfile = Gemfile('gem "rake", ">= 0.8.7", "<= 0.9.2"')
        self.assertEquals(gemfile.dependencies[0].name, 'rake')
        self.assertEquals(gemfile.dependencies[0].requirements, [">= 0.8.7", "<= 0.9.2"])

    def test_gem_with_options(self):
        gemfile = Gemfile('gem "rake", ">= 0.8.7", :require => false')
        self.assertEquals(gemfile.dependencies[0].name, 'rake')
        self.assertEquals(gemfile.dependencies[0].requirements, [">= 0.8.7"])
        self.assertEquals(gemfile.dependencies[0].options, {'require': 'false'})

    # ----

    def test_gems_of_type(self):
        gemfile = Gemfile('gem "rake"')
        self.assertEquals(gemfile.dependencies[0].type, "runtime")
        gemfile = Gemfile('gem "rake", :type => :development')
        self.assertEquals(gemfile.dependencies[0].type, "development")

    # ---

    def test_gems_of_a_group(self):
        gemfile = Gemfile('gem "rake"')
        self.assertEquals(gemfile.dependencies[0].groups, ["default"])
        gemfile = Gemfile('gem "rake", :group => :development')
        self.assertEquals(gemfile.dependencies[0].groups, ["development"])

    def test_gems_with_multiple_groups(self):
        gemfile = Gemfile('gem "rake", :group => [:development, :test]')
        self.assertEquals(gemfile.dependencies[0].groups, ["development", "test"])

    def test_parses_parentheses(self):
        gemfile = Gemfile('gem("rake", ">= 0.8.7")')
        self.assertEquals(gemfile.dependencies[0].name, 'rake')
        self.assertEquals(gemfile.dependencies[0].requirements, [">= 0.8.7"])

    def test_line_comments(self):
        gemfile = Gemfile('gem("rake", ">= 0.8.7")  # Comment')
        self.assertEquals(gemfile.dependencies[0].name, 'rake')
        self.assertEquals(gemfile.dependencies[0].requirements, [">= 0.8.7"])

    # def test_odd_quotes(self):
    #     gemfile = Gemfile('gem %q<rake>, ">= 0.8.7"')
    #     self.assertEquals(gemfile.dependencies[0].name, 'rake')
    #     self.assertEquals(gemfile.dependencies[0].requirements, [">= 0.8.7"])

import torch

def double_data(a,b,c,d,e,f):
      return torch.cat((b,c))

def double_labels(a,b,c,d,e,f):
      y1 = torch.zeros(b.shape[0])
      y2 = torch.ones(c.shape[0])
      return (torch.cat((y1,y2),dim=0).clone().detach()).to(torch.int64)

def triple_data(a,b,c,d,e,f):
      return torch.cat((a,b,c))

def triple_labels(a,b,c,d,e,f):
      y_a = torch.zeros(a.shape[0])
      y_b = torch.ones(b.shape[0])
      y_c = torch.ones(c.shape[0])*2
      return (torch.cat((y_a,y_b,y_c),dim=0).clone().detach()).to(torch.int64)

def quad_data(a,b,c,d,e,f):
      return torch.cat((a,b,c,d,e,f))

def quad_labels(a,b,c,d,e,f):
      a_labels = torch.zeros(a.shape[0])
      b_labels = torch.ones(b.shape[0])
      c_labels = torch.ones(c.shape[0])
      d_labels = torch.ones(d.shape[0])*2
      e_labels = torch.ones(e.shape[0])*2
      f_labels = torch.ones(f.shape[0])*3
      return (torch.cat((a_labels,b_labels,c_labels,d_labels,e_labels,f_labels),dim=0)).to(torch.int64)

def base_data(a,b,c,d,e,f):
      return torch.cat((a,b,c,d,e,f))

def base_labels(a,b,c,d,e,f):
      a_labels = torch.zeros(a.shape[0])
      b_labels = torch.ones(b.shape[0])
      c_labels = torch.ones(c.shape[0])*2
      d_labels = torch.ones(d.shape[0])*3
      e_labels = torch.ones(e.shape[0])*4
      f_labels = torch.ones(f.shape[0])*5
      return (torch.cat((a_labels,b_labels,c_labels,d_labels,e_labels,f_labels),dim=0)).to(torch.int64)

class MultiDataset(torch.utils.data.Dataset):
      def __init__(self, data:list,num_classes:int):

            if num_classes == 2:
                  self.data = double_data(*data)
                  self.label = double_labels(*data)
            elif num_classes == 3:
                  self.data = triple_data(*data)
                  self.label = triple_labels(*data)
            elif num_classes == 4:
                  self.data = quad_data(*data)
                  self.label = quad_labels(*data)
            elif num_classes == 6:
                  self.data = base_data(*data)
                  self.label = base_labels(*data)


      def __len__(self):
            return len(self.label)

      def __getitem__(self, index):
            X = self.data[index]
            y = self.label[index]
            return X, y

